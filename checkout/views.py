from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.views import View
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.mixins import UserPassesTestMixin
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
    """
    This view displays an Order Form to the user, pre-populated if the user
    has previously saved their order profile. It creates a Stripe payment
    intent for the order, and passes the Stripe public key and client secret
    to the page so that the payment form can be submitted by stripe_payments.js
    """
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
    """
    This view accepts a POST request from stripe_payments.js which contains
    the order form data and the save-info flag that the user can set to
    request that their order profile be saved. It creates the order in the
    database, and modifies the paymentIntent metadata so that it contains
    the order_number, user email (not stored in Stripe shipping attribute), the
    value of the save-info flag and a JSON encoded summary of the basket.
    """
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

            # Create a dictionary from the basket summary, and convert
            # all Decimal amounts to ints, as these objects
            # can't be JSON-serialized and sent with the metadata to Stripe.
            basket_dict = {}
            basket_dict['items'] = []
            for item in basket_summary['basket_items']:
                copy = {}
                copy['id'] = item['id']
                copy['quantity'] = item['quantity']
                copy['item_cost'] = int(item['item_cost'] * 100)
                basket_dict['items'].append(copy)
            basket_dict['subtotal'] = int(basket_summary['subtotal'] * 100)
            basket_dict['delivery'] = int(basket_summary['delivery'] * 100)
            basket_dict['total'] = int(basket_summary['total'] * 100)
            basket_dict['discount'] = int(basket_summary['discount'] * 100)
            metadata = {
                'email': data['email'],
                'order_number': order.order_number,
                'save_personal_info': save_info,
                'basket_summary': json.dumps(basket_dict),
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
    """
    This view accepts a POST request from stripe_payments.js when the Stripe
    confirmPayment promise is fulfilled. It retrieves the order, sets the
    payment confirmed flag to True and sends an email to the customer
    confirming that the order will shortly be dispatched.
    """
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
            item_str = \
                ''.join([f'{i.product.name} x {i.quantity}\n' for i in items])

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

            # Empty the shopping basket before redirecting
            if request.session['basket']:
                request.session['basket'] = {}

        return HttpResponseRedirect(redirect_url)


class CheckoutSucceededView(View):
    """
    This view is displayed when Stripe, having successfully completed the
    payment process, fulfills the promise in stripe_payments.js which
    then sets the window.location attribute to the 'checkout_succeeded' url.
    It allows the user to view a summary of their order and their delivery
    details.
    """
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


class StaffOrderList(UserPassesTestMixin, View):
    """
    This view, available only to staff, displays a list of all orders in the
    database, ordered by date, whether or not they are fulfilled, and whether
    or not their payment in confirmed. Unfulfilled orders with confirmed
    payments appear at the top of the list, ordered by ascending date.
    """
    def get(self, request):
        orders = Order.objects.all().order_by(
            '-payment_confirmed',
            'fulfilled',
            'date',
            )

        context = {
            'orders': orders,
        }
        return render(request, 'checkout/staff_order_list.html', context)

    def test_func(self):
        return self.request.user.is_staff


class StaffOrderDetail(UserPassesTestMixin, View):
    """
    This view is available only to staff.
    """
    def get(self, request, order_id):
        """ Displays the details of the specified order """
        order = get_object_or_404(Order, pk=order_id)
        line_items = order.items.all()
        context = {
            'order': order,
            'line_items': line_items,
        }
        return render(request, 'checkout/staff_order_detail.html', context)

    def post(self, request):
        """ Marks the order specified in the POST request as fulfilled """
        id = int(request.POST.get('fulfilled'))
        order = get_object_or_404(Order, pk=id)
        order.fulfilled = True
        order.save()

        return redirect(reverse('staff_order_list'))

    def test_func(self):
        return self.request.user.is_staff
