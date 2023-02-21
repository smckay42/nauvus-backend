import json
import time

import pytest
import stripe
from django.conf import settings
from rest_framework.test import APITestCase

from nauvus.apps.loads.models import Load
from nauvus.apps.payments.models import Payment
from nauvus.apps.webhooks.models import ProcessedStripeEvent
from nauvus.services.credit.oatfi.api import Oatfi
from nauvus.services.stripe import StripeClient
from nauvus.utils.testing import create_stripe_checkout_session_event

DUMMY_WEBHOOK_PAYLOAD = """{
  "id": "evt_test_webhook",
  "object": "event"
}"""

DUMMY_WEBHOOK_SECRET = "whsec_test_secret"


def generate_header(**kwargs):
    timestamp = kwargs.get("timestamp", int(time.time()))
    payload = kwargs.get("payload", DUMMY_WEBHOOK_PAYLOAD)
    secret = kwargs.get("secret", DUMMY_WEBHOOK_SECRET)
    scheme = kwargs.get("scheme", stripe.WebhookSignature.EXPECTED_SCHEME)
    signature = kwargs.get("signature", None)
    if signature is None:
        payload_to_sign = "%d.%s" % (timestamp, payload)
        signature = stripe.WebhookSignature._compute_signature(payload_to_sign, secret)
    header = "t=%d,%s=%s" % (timestamp, scheme, signature)
    return header


@pytest.mark.usefixtures("load_for_testclass", "carrier_user_for_testclass")
class TestStripeWebhook(APITestCase):
    oatfi = Oatfi()
    stripe = StripeClient()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = "/api/v1/webhooks/stripe-webhooks/"

    def setUp(self) -> None:

        self.carrier_user.user.save()
        self.carrier_user.carrier.save()
        self.carrier_user.save()
        self.carrier_driver.driver.user.save()
        self.carrier_driver.driver.save()
        self.carrier_driver.save()
        self.load.broker.save()
        self.load.current_status = Load.Status.DELIVERED
        self.load.driver = self.carrier_driver.driver
        self.load.save()
        self.load_settlement.save()
        self.invoice.carrier_user = self.carrier_user

        # set up the stripe links
        amount_due = int(float(self.load.final_rate) * 100)  # cents
        stripe_payment_link = self.stripe.get_payment_link(amount_due, self.load.id)
        self.invoice.stripe_payment_link = stripe_payment_link.get("url")
        self.invoice.stripe_payment_id = stripe_payment_link.get("id")
        self.invoice.save()

        self.oatfi.save_carrier(self.carrier_user)
        self.oatfi.send_invoice_history([self.invoice])

        line_items = stripe.PaymentLink.list_line_items(stripe_payment_link.get("id"))

        self.price_id = line_items["data"][0]["price"]["id"]

        self.checkout_session = stripe.checkout.Session.create(
            success_url="https://stripe.com",
            cancel_url="https://stripe.com",
            mode="payment",
            line_items=[{"price": self.price_id, "quantity": 1}],
        )

    def tearDown(self) -> None:
        stripe.checkout.Session.expire(self.checkout_session["id"])

    @pytest.mark.django_db
    def test_checkout_session_completed(self):
        event_time = int(time.time())

        event = create_stripe_checkout_session_event(
            self.invoice,
            self.stripe.EventTypes.CHECKOUT_SESSION_COMPLETED,
            event_time,
            self.checkout_session["id"],
            self.checkout_session["payment_intent"],
        )
        event_id = event["id"]
        event = json.dumps(event)

        header = generate_header(
            payload=event, secret=settings.STRIPE_ENDPOINT_SECRET, timestamp=event_time, scheme="v1"
        )

        response = self.client.post(self.url, data=event, content_type="application/json", HTTP_STRIPE_SIGNATURE=header)
        self.assertEqual(response.status_code, 200)

        # invoice status should be "checkout_complete"
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, "checkout_complete")

        event_record = ProcessedStripeEvent.objects.get(pk=event_id)

        self.assertIsNotNone(event_record)

        response = self.client.post(self.url, data=event, content_type="application/json", HTTP_STRIPE_SIGNATURE=header)
        self.assertEqual(response.status_code, 200)

        # TODO: add a check to ensure that the event did not get processed again

    @pytest.mark.django_db
    def test_checkout_session_payment_succeeded_on_instantpay(self):

        # create a loan for this load so that it can be triggered and repaid
        loan = self.oatfi.get_loan_offer(self.invoice)
        loan.save()

        self.oatfi.accept_loan(loan)

        event_time = int(time.time())

        event = create_stripe_checkout_session_event(
            self.invoice,
            self.stripe.EventTypes.CHECKOUT_SESSION_ASYNC_PAYMENT_SUCCEEDED,
            event_time,
            self.checkout_session["id"],
            self.checkout_session["payment_intent"],
        )
        event_id = event["id"]
        event = json.dumps(event)

        header = generate_header(
            payload=event, secret=settings.STRIPE_ENDPOINT_SECRET, timestamp=event_time, scheme="v1"
        )

        response = self.client.post(self.url, data=event, content_type="application/json", HTTP_STRIPE_SIGNATURE=header)
        self.assertEqual(response.status_code, 200)

        # check the db for the payment record
        broker_payment = Payment.objects.get(
            payment_type=Payment.PaymentType.FROM_BROKER, stripe_ref_id=self.checkout_session["payment_intent"]
        )

        self.assertIsNotNone(broker_payment)

        event_record = ProcessedStripeEvent.objects.get(pk=event_id)

        self.assertIsNotNone(event_record)

        # check the load settlement for the payments and correct status
        self.load.refresh_from_db()

        self.assertEquals(self.load.current_status, Load.Status.COMPLETED)

    @pytest.mark.django_db
    def test_checkout_session_payment_succeeded_without_instantpay(self):
        event_time = int(time.time())

        event = create_stripe_checkout_session_event(
            self.invoice,
            self.stripe.EventTypes.CHECKOUT_SESSION_ASYNC_PAYMENT_SUCCEEDED,
            event_time,
            self.checkout_session["id"],
            self.checkout_session["payment_intent"],
        )
        event_id = event["id"]
        event = json.dumps(event)

        header = generate_header(
            payload=event, secret=settings.STRIPE_ENDPOINT_SECRET, timestamp=event_time, scheme="v1"
        )

        response = self.client.post(self.url, data=event, content_type="application/json", HTTP_STRIPE_SIGNATURE=header)
        self.assertEqual(response.status_code, 200)

        # check the db for the payment record
        broker_payment = Payment.objects.get(
            payment_type=Payment.PaymentType.FROM_BROKER, stripe_ref_id=self.checkout_session["payment_intent"]
        )

        self.assertIsNotNone(broker_payment)

        event_record = ProcessedStripeEvent.objects.get(pk=event_id)

        self.assertIsNotNone(event_record)
