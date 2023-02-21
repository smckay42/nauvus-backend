from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser


class TestStripeAccountCreateLink(APITestCase):

    def setUp(self):
        self.stripe_url = "/api/v1/users/create-account-links/"

        self.user_dispatcher = get_user_model().objects.create_user(username="dispatcher_test",
                                                                    first_name="Dispatcher Testing Inc.",
                                                                    email="dispatcher_test@mail.com",
                                                                    password='somestrongpass2022',
                                                                    stripe_customer_id='acct_1M837JRi0EawehPg')
        self.dispatcher = Dispatcher.objects.create(organization_name='Dispatcher Testing Inc.')
        self.dispatcher_user = DispatcherUser.objects.create(user=self.user_dispatcher, dispatcher=self.dispatcher)

    def test_stripe_account_links_returns_200(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        payload = {
            "refresh_url": "https://staging.nauvus.com/manage-profile/onboarding-tasks?resendStripeDetails=true",
            "return_url": "https://staging.nauvus.com/manage-profile/onboarding-tasks"
        }
        response = self.client.post(self.stripe_url, data=payload)
        self.assertEqual(response.status_code, 200)

    def test_stripe_account_links_payload_contains_object(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        payload = {
            "refresh_url": "https://staging.nauvus.com/manage-profile/onboarding-tasks?resendStripeDetails=true",
            "return_url": "https://staging.nauvus.com/manage-profile/onboarding-tasks"
        }
        response = self.client.post(self.stripe_url, data=payload)
        self.assertEqual(response.data['object'], 'account_link')
