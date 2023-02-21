import datetime

import pytest
from rest_framework.test import APITestCase

from nauvus.apps.loads.models import Load


@pytest.mark.usefixtures("load_for_testclass", "carrier_user_for_testclass")
class TestPaymentDetails(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.payment_url_base = "/api/v1/payments"
        return super().setUpTestData()

    def setUp(self) -> None:

        # saving the broker and the carrier will ensure they are already in Oatfi
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
        self.invoice.save()

        self.client.force_authenticate(user=self.carrier_user.user)

        return super().setUp()

    @pytest.mark.django_db
    def test_get_available_payment_types(self):

        load_id = str(self.load.id)
        url = f"{self.payment_url_base}/{load_id}/types/"
        result = self.client.get(url, format="json")

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, {"instant": True})

    @pytest.mark.django_db
    def test_get_payment_details_instant_and_accept(self):

        load_id = str(self.load.id)
        url = f"{self.payment_url_base}/{load_id}/details/?instant=true"

        result = self.client.get(url, format="json")

        self.assertEqual(result.status_code, 200)
        self.assertGreater(result.data["available_today"], 0)

        url = f"{self.payment_url_base}/{load_id}/accept/"

        payload = {
            "instant_payment": "true",
            "terms_accepted": "true",
            "terms_accepted_timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }

        result = self.client.post(url, data=payload, format="json")

        self.assertEqual(result.status_code, 200)
        self.assertIn("payment_id", result.data)

    @pytest.mark.django_db
    def test_get_payment_details_delayed(self):

        load_id = str(self.load.id)
        url = f"{self.payment_url_base}/{load_id}/details/"

        result = self.client.get(url, format="json")

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data["available_today"], 0)
        self.assertGreater(result.data["available_on_broker_payment"], 0)

    @pytest.mark.django_db
    def test_payment_permission(self):
        load_id = str(self.load.id)
        url = f"{self.payment_url_base}/{load_id}/types/"

        self.load.current_status = Load.Status.BOOKED
        self.load.save()
        result = self.client.get(url, format="json")

        self.assertEqual(result.status_code, 403)

        self.load.current_status = Load.Status.DELIVERED
        self.load.driver = None
        self.load.save()

        result = self.client.get(url, format="json")

        self.assertEqual(result.status_code, 403)

    def test_accept_regular_payment(self):
        load_id = str(self.load.id)

        url = f"{self.payment_url_base}/{load_id}/accept/"

        payload = {
            "terms_accepted": "true",
            "terms_accepted_timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }

        result = self.client.post(url, data=payload, format="json")
        self.assertEqual(result.status_code, 200)
