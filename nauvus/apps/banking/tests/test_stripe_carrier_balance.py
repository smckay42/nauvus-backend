import pytest
from rest_framework.test import APITestCase

from nauvus.apps.loads.models import Load


@pytest.mark.usefixtures("load_for_testclass", "carrier_user_for_testclass")
class TestCarrierBalance(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.url_base = "/api/v1/banking"
        return super().setUpTestData()

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
        self.invoice.save()

        self.client.force_authenticate(user=self.carrier_user.user)

        return super().setUp()

    @pytest.mark.django_db
    def test_carrier_get_balance(self):

        url = f"{self.url_base}/balance/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_carrier_get_external_account_details(self):

        url = f"{self.url_base}/external-account-info/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("bank_name", response.data)
        self.assertIn("account_num_last4", response.data)
