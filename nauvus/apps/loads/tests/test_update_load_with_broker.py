from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.apps.loads.models import Load


class TestUpdateBrokerInLoadAPI(APITestCase):

    def setUp(self):
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
                                                           password='somestrongpass2022', user_type='dispatcher')
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
            current_status="available",
            details={"weight": "345", "commodity": "Soy", "length": "100", "trailer_type": "Van"},
            contact={"info": "", "phone": "123456789", "email": "test@email.com", "reference_number": "123984",
                     "notes": ""},
            posted_rate=Decimal(1000),
            dispatcher=self.dispatcher_user,
            created_by=self.user,
        )

    def test_update_load_returns_200(self):
        self.client.force_authenticate(user=self.user)
        expected_json = {
            "posted_rate": Decimal(2000)
        }
        response = self.client.patch(f"{self.load_url}{self.load.id}/", data=expected_json, format="json")
        self.assertEqual(response.status_code, 200)

    def test_update_load_check_content(self):
        self.client.force_authenticate(user=self.user)
        expected_json = {
            "posted_rate": Decimal(2000),
            "details": {"weight": "345", "commodity": "Cars", "length": "100", "trailer_type": "Van"},
        }
        response = self.client.patch(f"{self.load_url}{self.load.id}/", data=expected_json, format="json")
        data = response.json()
        self.assertEqual(data.get("data").get("posted_rate"), "2000.00")
        self.assertEqual(data.get("data").get("details").get("commodity"), "Cars")
