from django.conf import settings
from django.http import HttpResponse
from django.views import View
from checkout.webhook_handler import StripeWH_Handler
import stripe


class WebhookView(View):
    """
    Listens for webhooks from Stripe. Follows closely the webhooks.py class
    in Boutique Ado.
    """
    def post(self, request):
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        stripe.api_key = settings.STRIPE_PRIVATE_KEY
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            # Invalid payoad
            return HttpResponse(content='Invalid payload', status=400)
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return HttpResponse(content='Invalid signature', status=400)
        except Exception as e:
            return HttpResponse(content=f'error = {e}', status=400)

        # Set up a webhook handler
        handler = StripeWH_Handler(request)

        # Map webhook events to relevant handler functions
        event_map = {
            'payment_intent.succeeded':
            handler.handle_payment_intent_succeeded,
            'payment_intent.payment_failed':
            handler.handle_payment_intent_failed,
            'checkout.session.completed':
            handler.handle_checkout_session_completed,
            'invoice.paid': handler.handle_invoice_paid,
            'invoice.payment_failed': handler.handle_invoice_payment_failed,
        }

        # Get the webhook type from Stripe
        event_type = event['type']

        # Get the handler from the event_map, if one exists. Use generic
        # handler by default.
        event_handler = event_map.get(event_type, handler.handle_event)

        # Call the event handler with the event
        response = event_handler(event)
        return response
