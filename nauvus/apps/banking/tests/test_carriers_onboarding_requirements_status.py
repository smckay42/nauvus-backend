import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.carrier.models import Carrier, CarrierUser, CarrierFleetApplication, CarrierW9Information, \
    CarrierServiceAgreement


class TestCarrierUserRequirementRetrieve(APITestCase):

    def setUp(self):
        self.url = "/api/v1/users/user-onboarding-requirements-status/"

        self.user = get_user_model().objects.create_user(username="carrier_test", first_name="Carrier",
                                                         last_name='Testing', email="carrier_demo@demo.com",
                                                         password='somestrongpass2022', user_type='carrier_owner',
                                                         stripe_customer_id='acct_1LazCiDGo3FX5nif')

        self.carrier = Carrier.objects.create(organization_name='Carrier Testing Inc.', street1='Carrier St.',
                                              street2='', city='Atlanta', state='GA', zip_code='98765',
                                              mc_number='123456789', fleet_id='123456789', dot_number='123456789')
        self.carrier_user = CarrierUser.objects.create(user=self.user, carrier=self.carrier,
                                                       is_current_organization=True)

        CarrierFleetApplication.objects.create(carrier=self.carrier)
        CarrierW9Information.objects.create(carrier=self.carrier)
        CarrierServiceAgreement.objects.create(carrier=self.carrier, is_signed=True)

    def test_carrier_requirements_status_returns_200(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_carrier_requirements_status_contains_object(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertTrue(response.json()['data']['w9_information'])
        self.assertTrue(response.json()['data']['fleet_application'])
        self.assertTrue(response.json()['data']['service_agreement'])

    def test_carrier_requirements_status_service_agreement_not_signed(self):
        CarrierServiceAgreement.objects.filter(carrier=self.carrier).update(is_signed=False)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertTrue(response.json()['data']['w9_information'])
        self.assertTrue(response.json()['data']['fleet_application'])
        self.assertFalse(response.json()['data']['service_agreement'])


