import logging
from abc import abstractmethod
from typing import final

from django.core.exceptions import ObjectDoesNotExist

from nauvus.apps.loads.models import Load
from nauvus.apps.payments.models import Payment
from nauvus.apps.payments.services import process_broker_payment
from nauvus.apps.webhooks.models import ProcessedStripeEvent
from nauvus.services.stripe import StripeClient

stripe_client = StripeClient()
logger = logging.getLogger(__name__)


class StripeEventHandler:
    """Abstract base class for handling events from Stripe.  Children should implement `handle_event`"""

    def __init__(self, event):
        self.event_id = event["id"]
        self.object = event["data"]["object"]

    @abstractmethod
    def handle_event(self):
        pass

    @final
    def handle(self):
        try:
            ProcessedStripeEvent.objects.get(pk=self.event_id)
            # if the event has already been processed than return and do nothing
            logger.debug(f"Previously processed Stripe event with id {self.event_id}.  Doing nothing.")
            return
        except ObjectDoesNotExist:
            pass
        logger.debug(f"Received stripe event with id {self.event_id}.  ")
        self.handle_event()
        # once processing the event is complete, store it in the database so that it will not be re-run
        ProcessedStripeEvent.objects.create(stripe_event_id=self.event_id)


class CheckoutSessionCompletedEventHandler(StripeEventHandler):
    """processes the checkout session complete event and marks the payment link inactive so it cant be used again"""

    def handle_event(self):
        logger.debug(f"Handling checkout session complete for event {self.event_id}")
        # archive the price & paymentlink
        checkout_session_id = self.object["id"]

        price_id = stripe_client.get_price_id_from_checkout_session(checkout_session_id)
        stripe_client.archive_price(price_id)
        stripe_client.archive_paymentlink(self.object["payment_link"])
        load_id = self.object["metadata"]["load_id"]
        load = Load.objects.get(id=load_id)
        invoice = load.loadsettlement.invoice

        # if the invoice has not already been marked as paid, mark it as checkout complete
        if invoice.status != "paid":
            invoice.status = "checkout_complete"
            invoice.save()


class CheckoutSessionPaymentSucceededEventHandler(StripeEventHandler):
    def handle_event(self):
        # handle the payouts
        logger.debug(f"Handling checkout payment succeeded for event {self.event_id}")
        load_id = self.object["metadata"]["load_id"]
        load = Load.objects.get(id=load_id)
        invoice = load.loadsettlement.invoice

        # create the payment and reference the payment intent
        payment = Payment.objects.create(
            payment_type=Payment.PaymentType.FROM_BROKER,
            amount_in_cents=self.object["amount_total"],
            load_settlement=load.loadsettlement,
            stripe_ref_id=self.object["payment_intent"],
        )

        process_broker_payment(invoice, payment)
