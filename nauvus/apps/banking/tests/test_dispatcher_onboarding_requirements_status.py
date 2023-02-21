from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser, DispatcherW9Information, \
    DispatcherServiceAgreement


class TestDispatcherRequirementStatus(APITestCase):

    def setUp(self):
        self.stripe_url = "/api/v1/users/user-onboarding-requirements-status/"

        self.user_dispatcher = get_user_model().objects.create_user(username="dispatcher_test",
                                                                    first_name="Dispatcher Testing Inc.",
                                                                    email="dispatcher_test@mail.com",
                                                                    password='somestrongpass2022',
                                                                    stripe_customer_id='acct_1LazCiDGo3FX5nif',
                                                                    user_type='dispatcher')
        self.dispatcher = Dispatcher.objects.create(organization_name='Dispatcher Testing Inc.')
        self.dispatcher_user = DispatcherUser.objects.create(user=self.user_dispatcher, dispatcher=self.dispatcher)

        DispatcherW9Information.objects.create(dispatcher=self.dispatcher)
        DispatcherServiceAgreement.objects.create(dispatcher=self.dispatcher, is_signed=True)

    def test_dispatcher_requirements_status_returns_200(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        response = self.client.get(self.stripe_url)
        self.assertEqual(response.status_code, 200)

    def test_dispatcher_requirements_status_contains_object(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        response = self.client.get(self.stripe_url)
        self.assertTrue(response.json()['data']['w9_information'])
        self.assertTrue(response.json()['data']['service_agreement'])

    def test_dispatcher_requirements_status_service_agreement_not_signed(self):
        DispatcherServiceAgreement.objects.filter(dispatcher=self.dispatcher).update(is_signed=False)
        self.client.force_authenticate(user=self.user_dispatcher)
        response = self.client.get(self.stripe_url)
        self.assertTrue(response.json()['data']['w9_information'])
        self.assertFalse(response.json()['data']['service_agreement'])
