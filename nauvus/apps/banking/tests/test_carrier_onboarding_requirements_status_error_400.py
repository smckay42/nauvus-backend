from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.carrier.models import Carrier, CarrierUser, CarrierFleetApplication, CarrierW9Information, \
    CarrierServiceAgreement


class TestStripeUserRequirementRetrieveError400(APITestCase):

    def setUp(self):
        self.url = "/api/v1/users/user-onboarding-requirements-status/"

        self.user = get_user_model().objects.create_user(username="carrier_test", first_name="Carrier",
                                                         last_name='Testing', email="carrier_demo@demo.com",
                                                         password='somestrongpass2022', user_type='carrier_owner',
                                                         stripe_customer_id='acct_1LazCiDGo3FX5n')

        self.carrier = Carrier.objects.create(organization_name='Carrier Testing Inc.', street1='Carrier St.',
                                              street2='', city='Atlanta', state='GA', zip_code='98765',
                                              mc_number='123456789', fleet_id='123456789', dot_number='123456789')
        self.carrier_user = CarrierUser.objects.create(user=self.user, carrier=self.carrier,
                                                       is_current_organization=True)

        CarrierFleetApplication.objects.create(carrier=self.carrier)
        CarrierW9Information.objects.create(carrier=self.carrier)
        CarrierServiceAgreement.objects.create(carrier=self.carrier)

    def test_dispatcher_requirements_returns_400_stripe_customer_id_does_not_exist(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
