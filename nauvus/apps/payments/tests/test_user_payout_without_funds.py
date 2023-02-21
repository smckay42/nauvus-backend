from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.carrier.models import CarrierUser, Carrier


class TestUserPayout(APITestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/payments/users-payouts/"

        self.user = get_user_model().objects.create_user(username="carrier_test", first_name="Carrier Testing",
                                                         email="justin+carrier2@nauvus.com",
                                                         password='somestrongpass2022', user_type='carrier_owner',
                                                         stripe_customer_id="acct_1MJhKMDBHKrWsQOU")
        self.carrier = Carrier.objects.create(organization_name='Carrier Testing Inc.', street1='Carrier St.',
                                              street2='', city='Atlanta', state='GA', zip_code='987654321')
        self.carrier_user = CarrierUser.objects.create(user=self.user, carrier=self.carrier,
                                                       is_current_organization=True, access_type='full_admin')

    def test_user_with_insufficient_funds_returns_400(self):
        self.client.force_authenticate(user=self.user)
        expected_json = {"amount": Decimal(1500.50)}
        response = self.client.post(self.url, data=expected_json)
        self.assertEqual(response.status_code, 400)
