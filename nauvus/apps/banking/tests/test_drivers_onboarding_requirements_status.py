import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.carrier.models import Carrier, CarrierUser, CarrierFleetApplication, CarrierW9Information, \
    CarrierServiceAgreement
from nauvus.apps.driver.models import Driver, DriverServiceAgreement


class TestCarrierUserRequirementRetrieve(APITestCase):

    def setUp(self):
        self.url = "/api/v1/users/user-onboarding-requirements-status/"

        self.user = get_user_model().objects.create_user(username="driver_test", first_name="Driver Testing",
                                                           email="driver_demo@demo.com",
                                                           password='somestrongpass2022', user_type='driver')
        self.driver = Driver.objects.create(user=self.user)
        DriverServiceAgreement.objects.create(driver=self.driver, is_signed=True)

    def test_driver_requirements_status_returns_200(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_driver_requirements_status_contains_object(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertTrue(response.json()['data']['service_agreement'])

    def test_driver_requirements_status_service_agreement_not_signed(self):
        DriverServiceAgreement.objects.filter(driver=self.driver).update(is_signed=False)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertFalse(response.json()['data']['service_agreement'])


