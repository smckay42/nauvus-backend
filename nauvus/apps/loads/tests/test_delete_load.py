from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.apps.loads.models import Load


class TestCreateLoadAPI(APITestCase):

    def setUp(self):
        self.load_url = "/api/v1/loads/"

        # Create a super user to delete loads
        self.admin_user = get_user_model().objects.create_user(username="admin",
                                                               first_name="Nauvus Admin",
                                                               email="nauvus_admin@demo.com",
                                                               password='somestrongpass2022',
                                                               is_superuser=True)

        self.user = get_user_model().objects.create_user(username="dispatcher_test",
                                                                    first_name="Dispatcher Testing",
                                                                    email="dispatcher_demo@demo.com",
                                                                    password='somestrongpass2022',
                                                                    user_type='dispatcher')
        self.dispatcher = Dispatcher.objects.create(organization_name='Dispatcher Testing Inc.')
        self.dispatcher_user = DispatcherUser.objects.create(user=self.user, dispatcher=self.dispatcher)


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
                     "notes": ""}, posted_rate=Decimal(1000),
            dispatcher=self.dispatcher_user,
        )

    def test_delete_load_user_is_not_admin_returns_403(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"{self.load_url}{self.load.id}/")
        self.assertEqual(response.status_code, 403)

    def test_delete_load__user_is_not_authenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(f"{self.load_url}{self.load.id}/")
        self.assertEqual(response.status_code, 401)

    def test_delete_load_returns_204(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f"{self.load_url}{self.load.id}/")
        self.assertEqual(response.status_code, 204)
