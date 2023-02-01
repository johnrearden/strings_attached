from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.views import View
from django.conf import settings
from .forms import OrderForm
from basket.contexts import basket_contents

import stripe


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
