from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views import View
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import OrderForm
from .models import Order, OrderLineItem, UserOrderProfile
from products.models import Product
from basket.contexts import basket_contents

import stripe
import json


class CheckoutView(View):
    def get(self, request):
        basket = request.session.get('basket', {})
        if not basket:
            messages.error(request, 'There\'s nothing in your basket!')
            return redirect(reverse('product_display'))

        # Get the total payment amount from the basket
        current_basket = basket_contents(request)
        payment_total = current_basket['total']
        stripe_total = round(payment_total * 100)

        # Create the Stripe payment intent
        stripe.api_key = settings.STRIPE_PRIVATE_KEY
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
            automatic_payment_methods={"enabled": True},
        )

        # Populate the order form if the user has a UserOrderProfile
        if request.user.is_anonymous:
            order_form = OrderForm()
        else:
            order_profile = UserOrderProfile.objects.filter(user=request.user)
            if order_profile:
                prof = order_profile[0]
                data = {
                    'full_name': prof.full_name,
                    'email': prof.email,
                    'phone_number': prof.phone_number,
                    'country': prof.country,
                    'postcode': prof.postcode,
                    'town_or_city': prof.town_or_city,
                    'street_address1': prof.street_address1,
                    'street_address2': prof.street_address2,
                    'county': prof.county,
                }
                order_form = OrderForm(initial=data)
            else:
                order_form = OrderForm()
        template = 'checkout/checkout.html'
        context = {
            'order_form': order_form,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'stripe_client_secret': intent.client_secret,
        }

        return render(request, template, context)


class SaveOrderView(APIView):
    def post(self, request):
        data = request.POST
        basket_summary = basket_contents(request)
        basket = request.session.get('basket', {})
        form_data = {
            'full_name': data['full_name'],
            'email': data['email'],
            'phone_number': data['phone_number'],
            'country': data['country'],
            'postcode': data['postcode'],
            'town_or_city': data['town_or_city'],
            'street_address1': data['street_address1'],
            'street_address2': data['street_address2'],
            'county': data['county'],
        }
        orderForm = OrderForm(form_data)
        if orderForm.is_valid():
            pid = request.POST.get('client_secret').split('_secret')[0]
            order = orderForm.save(commit=False)
            order.delivery_cost = basket_summary['delivery']
            order.discount = basket_summary['discount']
            order.order_total = basket_summary['subtotal']
            order.grand_total = basket_summary['total']
            order.pid = pid

            # Save the order, and then attach the order_number, save-info flag
            # and basket to the Stripe paymentIntent metadata before returning
            # to the checkout page to process the payment.
            order.save()

            # Create line items for each item in the basket.
            for id, quantity in basket.items():
                product = Product.objects.get(id=id)
                line_item = OrderLineItem.objects.create(order=order,
                                                         product=product,
                                                         quantity=quantity)
                line_item.save()

            save_info = '' if not data.get('save-info') else data['save-info']
            if save_info:
                profile = UserOrderProfile.objects.filter(user=request.user)
                if not profile:
                    UserOrderProfile.objects.create(
                        user=request.user,
                        full_name=order.full_name,
                        email=order.email,
                        phone_number=order.phone_number,
                        country=order.country,
                        postcode=order.postcode,
                        town_or_city=order.town_or_city,
                        street_address1=order.street_address1,
                        street_address2=order.street_address2,
                        county=order.county,
                    )
                else:
                    prof = profile[0]
                    prof.full_name = order.full_name
                    prof.email = order.email
                    prof.phone_number = order.phone_number
                    prof.country = order.country
                    prof.postcode = order.postcode
                    prof.town_or_city = order.town_or_city
                    prof.street_address1 = order.street_address1
                    prof.street_address2 = order.street_address2
                    prof.county = order.county
                    prof.save()

            metadata = {
                'order_number': order.order_number,
                'save_personal_info': save_info,
                'basket': json.dumps(basket),
            }
            stripe.api_key = settings.STRIPE_PRIVATE_KEY
            try:
                stripe.PaymentIntent.modify(
                    pid,
                    metadata=metadata)
            except Exception:
                print('cant save metadata in payment intent')
            return Response(status=status.HTTP_200_OK)


class PaymentConfirmedView(APIView):
    def post(self, request):
        if request.data['payment_confirmed'] == 'True':
            pid = request.data.get('client_secret').split('_secret')[0]
            stripe.api_key = settings.STRIPE_PRIVATE_KEY
            intent = stripe.PaymentIntent.retrieve(pid)
            order_number = intent.metadata.get('order_number')
            order = Order.objects.get(order_number=order_number)
            order.payment_confirmed = True
            order.save()

            # Send confirmation email to the customer
            addr_fields = [order.full_name, order.street_address1,
                           order.street_address2, order.town_or_city,
                           order.postcode, order.country]
            address = ''.join([f'{fd}\n' if fd else '' for fd in addr_fields])
            items = OrderLineItem.objects.filter(order=order)
            item_str = ''.join([f'{i.product.name} x {i.quantity}\n' for i in items])

            message = (f'Your order #{order_number} is confirmed, and will be '
                       f'dispatched shortly.\nYour order details are as '
                       f'follows -\nAddress :\n{address}\nItems :\n'
                       f'{item_str}\nEnjoy!!')
            send_mail(
                subject=f'Order #{order_number} confirmed',
                message=message,
                from_email=None,
                recipient_list={order.email},
            )
            redirect_url = f'/checkout/checkout_succeeded/{order_number}'
        return HttpResponseRedirect(redirect_url)


class CheckoutSucceededView(View):
    def get(self, request, order_number):
        order = Order.objects.get(order_number=order_number)
        line_items = OrderLineItem.objects.filter(order=order)
        item_count = sum([item.quantity for item in line_items])
        context = {
            'order': order,
            'order_line_items': line_items,
            'item_count': item_count,
        }
        return render(request, 'checkout/checkout_succeeded.html', context)
