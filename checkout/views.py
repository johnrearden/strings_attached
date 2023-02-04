from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views import View
from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import OrderForm
from .models import Order
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

        order_form = OrderForm()
        template = 'checkout/checkout.html'
        context = {
            'order_form': order_form,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'stripe_client_secret': intent.client_secret,
        }

        return render(request, template, context)

    def post(self, request):
        print(request.POST)


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
            metadata = {
                'order_number': order.order_number,
                'save_personal_info': data['save-info'],
                'basket': json.dumps(basket),
            }
            stripe.api_key = settings.STRIPE_PRIVATE_KEY
            try:
                stripe.PaymentIntent.modify(
                    pid,
                    metadata=metadata)
            except Exception:
                print('exception')
        return Response(status=status.HTTP_200_OK)


class PaymentConfirmed(APIView):
    def post(self, request):
        if request.data['payment_confirmed'] == 'True':
            pid = request.data.get('client_secret').split('_secret')[0]
            stripe.api_key = settings.STRIPE_PRIVATE_KEY
            intent = stripe.PaymentIntent.retrieve(pid)
            order_number = intent.metadata.get('order_number')
            order = Order.objects.get(order_number=order_number)
            order.payment_confirmed = True
            order.save()
        return HttpResponseRedirect(reverse('checkout_success'))


class CheckoutSuccess(View):
    def get(self, request):
        return render(request, 'checkout/checkout_success.html', {})
