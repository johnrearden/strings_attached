from django.http import HttpResponse
from video_lessons.models import UserLearningProfile


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
        print('Handling payment intent succeeded')
        return HttpResponse(status=200)

    def handle_payment_intent_failed(self, event):
        """ Handle the Stripe payment_intent.failed webhook """
        print('Handling payment intent failed')
        return HttpResponse('Handling payment intent failed')

    def handle_checkout_session_completed(self, event):
        """ Handle the Stripe checkout.session.completed webhook, which
            indicates that an initial payment has been received and a 
            subscription has been created. """
        print('Handling checkout session completed')
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
        print('Handling invoice paid')
        print(event.data)
        customer_id = event.data.object.customer
        subscription_id = event.data.object.subscription
        user_learning_profile = UserLearningProfile.objects.get(
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id
        )
        user_learning_profile.subscription_paid = True
        user_learning_profile.save()
        print(user_learning_profile)
        return HttpResponse('Handling invoice paid')

    def handle_invoice_payment_failed(self, event):
        """ Handle the Stripe invoice.payment_failed webhook, which
            indicates that a recurring payment has failed. """
        print('Handling invoice payment_failed')
        return HttpResponse('Handling invoice payment_failed')
