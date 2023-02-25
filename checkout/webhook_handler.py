from django.http import HttpResponse
from django.core.mail import send_mail
from video_lessons.models import UserLearningProfile
from .models import Order, OrderLineItem
from products.models import Product
from datetime import datetime
from decimal import Decimal
import json


class StripeWH_Handler:
    """ Handles Stripe Webhooks from both Stripe PaymentIntents (shop item
        purchases) and CheckoutSessions (subscriptions). Follows closely the
        webhook_handler class in Boutique Ado."""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """ Handle a webhook event other than those specifically coded
            below """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200,
        )

    def handle_payment_intent_succeeded(self, event):
        """ Handle the Stripe payment_intent.succeeded webhook """
        metadata = event.data.object.metadata
        shipping_data = event.data.object.shipping
        order_number = metadata.order_number
        order_set = Order.objects.filter(order_number=order_number)

        # If there is a corresponding order in the database, ensure that
        # the payment_confirmed flag is set. If not, set it.
        if order_set:
            order = order_set[0]
            order.payment_confirmed = True
            order.save()
            return HttpResponse(status=200)
        else:
            # There is not order on the system. Create one from the information
            # in the metadata.basket field
            data = json.loads(metadata.basket_summary)
            order = Order.objects.create(
                full_name=shipping_data.get('name', ''),
                phone_number=shipping_data.get('phone', ''),
                email=metadata['email'],
                country=shipping_data['address'].get('country', ''),
                postcode=shipping_data['address'].get('postal_code', ''),
                town_or_city=shipping_data['address'].get('city', ''),
                street_address1=shipping_data['address'].get('line1', ''),
                street_address2=shipping_data['address'].get('line2', ''),
                county=shipping_data.get('phone', ''),
                date=datetime.now(),
                delivery_cost=Decimal(data['delivery'] / 100),
                discount=Decimal(data['discount'] / 100),
                order_total=Decimal(data['subtotal'] / 100),
                grand_total=Decimal(data['total'] / 100),
                pid=event.data.object.id,
                payment_confirmed=True,
            )
            for item in data['items']:
                OrderLineItem.objects.create(
                    order=order,
                    product=Product.objects.get(pk=int(item['id'])),
                    quantity=item['quantity'],
                )
            return HttpResponse(status=200)

    def handle_payment_intent_failed(self, event):
        """ Handle the Stripe payment_intent.failed webhook """
        return HttpResponse(status=200)

    def handle_checkout_session_completed(self, event):
        """ Handle the Stripe checkout.session.completed webhook, which
            indicates that an initial payment has been received and a
            subscription has been created. """
        metadata = event.data.object.metadata
        profile_id = metadata.user_id
        user_learning_profile = UserLearningProfile.objects.get(pk=profile_id)
        customer_id = event.data.object.customer
        subscription_id = event.data.object.subscription
        user_learning_profile.subscriber = True
        user_learning_profile.stripe_customer_id = customer_id
        user_learning_profile.stripe_subscription_id = subscription_id
        user_learning_profile.save()

        return HttpResponse('Handling checkout session completed')

    def handle_invoice_paid(self, event):
        """ Handle the Stripe invoice.paid webhook, which indicates that
            a recurring payment has been made."""
        customer_id = event.data.object.customer
        subscription_id = event.data.object.subscription
        user_learning_profile = UserLearningProfile.objects.get(
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id
        )
        user_learning_profile.subscription_paid = True

        # Set/reset the expiration date on the subscription
        timestamp = event.data.object.lines.data[0].period.end
        expiration = datetime.utcfromtimestamp(timestamp)
        user_learning_profile.subscription_expiration_date = expiration
        user_learning_profile.save()
        return HttpResponse('Handling invoice paid')

    def handle_invoice_payment_failed(self, event):
        """ Handle the Stripe invoice.payment_failed webhook, which
            indicates that a recurring payment has failed. """
        customer_id = event.data.object.customer
        subscription_id = event.data.object.subscription
        user_learning_profile = UserLearningProfile.objects.get(
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id
        )
        user_learning_profile.subscription_paid = False

        # Send an email to the customer to let them know their payment has 
        # failed, with a link to their profile page to enable them to manage
        # their subscription with Stripe.
        email = user_learning_profile.user.email
        message = ('Hi! We\'d just like to let you know that a payment for'
                   ' your subscription to our Guitar School has failed. You'
                   ' can click the link below to visit your profile page.'
                   '\n')
        send_mail(
                subject='Subscription payment failed!',
                message=message,
                from_email=None,
                recipient_list={email},
            )

        return HttpResponse('Handling invoice payment_failed')
