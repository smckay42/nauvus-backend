from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.carrier.models import CarrierUser, Carrier
from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.apps.driver.models import Driver, CarrierDriver
from nauvus.apps.loads.models import Load


class TestListDriverLoad(APITestCase):
    def setUp(self):
        self.load_url = "/api/v1/loads/list-user-loads/"

        self.user = get_user_model().objects.create_user(username="carrier_test", first_name="Carrier Testing",
                                                         email="carrier_demo@demo.com", password='somestrongpass2022',
                                                         user_type='carrier_owner')

        self.user_2 = get_user_model().objects.create_user(username="driver_test", first_name="Driver Testing",
                                                           email="driver_demo@demo.com",
                                                           password='somestrongpass2022', user_type='driver')

        self.carrier = Carrier.objects.create(organization_name='Carrier Testing Inc.')
        self.carrier_user = CarrierUser.objects.create(user=self.user, carrier=self.carrier)

        self.driver = Driver.objects.create(user=self.user_2)

        self.driver_carrier = CarrierDriver.objects.create(driver=self.driver, carrier=self.carrier)

        self.load = Load.objects.create(
            origin={"address1": "Test St.", "address2": "Test", "city": "Atlanta", "state": "GA", "longitude": "123",
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
            created_by=self.user
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

    def test_list_user_load_returns_status_200(self):

        # created_by = self.user

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.load_url)
        self.assertEqual(response.status_code, 200)

    def test_list_user_load_returns_one_load(self):

        # created_by = self.user

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.load_url)
        self.assertEqual(response.json().get('data')[0].get('origin').get('city'), 'Atlanta')
        self.assertEqual(response.status_code, 200)
