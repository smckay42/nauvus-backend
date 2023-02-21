import logging

import stripe
from django.conf import settings
from rest_framework import status, views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from nauvus.apps.webhooks.handlers import (
    CheckoutSessionCompletedEventHandler,
    CheckoutSessionPaymentSucceededEventHandler,
)
from nauvus.services.stripe import StripeClient

logger = logging.getLogger(__name__)


class StripeWebhook(views.APIView):
    permission_classes = [AllowAny]

    event_handlers = {
        StripeClient.EventTypes.CHECKOUT_SESSION_COMPLETED: CheckoutSessionCompletedEventHandler,
        StripeClient.EventTypes.CHECKOUT_SESSION_ASYNC_PAYMENT_SUCCEEDED: CheckoutSessionPaymentSucceededEventHandler,
    }

    def __get_event_handler(cls, event):
        event_type = event["type"]
        handler = cls.event_handlers.get(event_type)
        if handler:
            this_handler = handler(event)
            return this_handler
        return None

    def post(self, request, *args, **kwargs):

        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

        payload = request.body

        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = StripeClient().construct_event(payload, sig_header, endpoint_secret)
            handler = self.__get_event_handler(event)
            if handler:
                handler.handle()
            else:
                event_type = event["type"]
                logger.info(f"No handler for Stripe event of type {event_type}")
        except ValueError as e:
            # Invalid payload
            logger.error(e)
            return Response(data={"messages": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            logger.error(e)
            return Response(
                data={"messages": "Invalid signature. No signatures found matching the expected signature for payload"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            # if another error is encountered, log it

            logger.error(e, exc_info=True)

        return Response(status=status.HTTP_200_OK)
