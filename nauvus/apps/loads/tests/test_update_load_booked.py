from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.apps.loads.models import Load


class TestUpdateLoadBookedAPI(APITestCase):

    def setUp(self):
        settings.ACCOUNT_EMAIL_VERIFICATION = (
            "optional"  # set email verification optional only for testcases
        )

        self.load_url = "/api/v1/loads/"

        self.user = get_user_model().objects.create_user(username="dispatcher_test",
                                                         first_name="Dispatcher Testing",
                                                         email="dispatcher_demo@demo.com",
                                                         password='somestrongpass2022', user_type='dispatcher')
        self.dispatcher = Dispatcher.objects.create(organization_name='Dispatcher Testing Inc.')
        self.dispatcher_user = DispatcherUser.objects.create(user=self.user, dispatcher=self.dispatcher)

        self.user_2 = get_user_model().objects.create_user(username="another_dispatcher",
                                                           first_name="Anohter Dispatcher Testing",
                                                           email="dispatcher_another@demo.com",
                                                           password='somestrongpassword2022', user_type='dispatcher')
        self.dispatcher_2 = Dispatcher.objects.create(organization_name='Dispatcher Another Inc.')
        self.dispatcher_user_2 = DispatcherUser.objects.create(user=self.user_2,
                                                               dispatcher=self.dispatcher_2)

        self.load = Load.objects.create(
            origin={"address1": "Test St.", "address2": "Test", "city": "New York", "state": "NY", "longitude": "123",
                    "latitude": "123", "zipcode": "123"},
            destination={"address1": "Test Destination St.", "address2": "Test", "city": "Miami", "state": "FL",
                         "longitude": "321", "latitude": "567", "zipcode": "123478"},
            pickup_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            dropoff_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
            current_status="booked",
            details={"weight": "345", "commodity": "Soy", "length": "100", "trailer_type": "Van"},
            contact={"info": "", "phone": "123456789", "email": "test@email.com", "reference_number": "123984",
                     "notes": ""},
            posted_rate=Decimal(1000),
            dispatcher=self.dispatcher_user
        )

    def test_update_load_user_is_not_authenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        expected_json = {
            "posted_rate": Decimal(2000),
            "details": {"weight": "345", "commodity": "Cars", "length": "100", "trailer_type": "Van"},
        }
        response = self.client.patch(f"{self.load_url}{self.load.id}/", data=expected_json, format="json")
        self.assertEqual(response.status_code, 401)

    def test_update_load_payload_without_current_status_return_status_code_400(self):
        self.client.force_authenticate(user=self.user)
        expected_json = {
            "posted_rate": Decimal(2000)
        }
        response = self.client.patch(f"{self.load_url}{self.load.id}/", data=expected_json, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('message'), 'You only can change the current status.')

    #
    def test_update_load_current_status_and_more_are_in_request_only_current_status_updated(self):
        self.client.force_authenticate(user=self.user)
        expected_json = {
            "posted_rate": Decimal(2000),
            "current_status": "pending",
        }
        response = self.client.patch(f"{self.load_url}{self.load.id}/", data=expected_json, format="json")
        data = response.json()
        self.assertEqual(data.get("data").get("posted_rate"), "1000.00")
        self.assertEqual(data.get("data").get("current_status"), "pending")

    def test_update_load_current_status_and_more_are_in_request_but_current_status_available_return_400(self):
        self.client.force_authenticate(user=self.user)
        expected_json = {
            "posted_rate": Decimal(2000),
            "current_status": "available",
        }
        response = self.client.patch(f"{self.load_url}{self.load.id}/", data=expected_json, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('message'), 'It not allowed to set status to available.')
