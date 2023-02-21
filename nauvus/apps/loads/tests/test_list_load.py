from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.apps.driver.models import Driver
from nauvus.apps.loads.models import Load


class TestCreateLoadAPI(APITestCase):

    def setUp(self):

        self.load_url = "/api/v1/loads/"

        self.user_dispatcher = get_user_model().objects.create_user(
            username="dispatcher_test",
            first_name="Dispatcher Testing",
            email="dispatcher_demo@demo.com",
            password='somestrongpass2022',
        )

        self.dispatcher = Dispatcher.objects.create(organization_name='Dispatcher Testing Inc.')
        self.dispatcher_user = DispatcherUser.objects.create(user=self.user_dispatcher, dispatcher=self.dispatcher)
        self.driver = Driver.objects.create(user=self.user_dispatcher)

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
            created_by=self.user_dispatcher,
            driver = self.driver
        )

        Load.objects.create(
            origin={"city": "NAMPA", "state": "ID", "zipcode": "83651", "address1": None, "address2": None,
                    "latitude": 43.58246, "longitude": -116.56374},
            destination={"city": "BUFFALO", "state": "NY", "zipcode": "14201", "address1": None, "address2": None,
                         "latitude": 42.87941, "longitude": -78.87749},
            pickup_date=(datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
            dropoff_date=(datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S"),
            current_status="booked",
            details={"weight": "345", "commodity": "Corn", "length": "100", "trailer_type": "Van"},
            contact={"info": "", "phone": "123456789", "email": "test@email.com", "reference_number": "123984",
                     "notes": ""},
            posted_rate=Decimal(5000),
            driver=self.driver
        )

    def test_get_loads_returns_200(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        response = self.client.get(self.load_url)
        self.assertEqual(response.status_code, 200)

    def test_get_loads_check_response(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        response = self.client.get(self.load_url)
        data = response.json()
        self.assertEqual(len(data.get('data').get('results')), 1)
        self.assertEqual(data.get('data').get('results')[0].get('current_status'), "available")

