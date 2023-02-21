from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.apps.loads.models import Load


class TestLoadFilters(APITestCase):
    def setUp(self):
        self.load_url = "/api/v1/loads/search/"

        self.user = get_user_model().objects.create_user(
            username="dispatcher_test",
            first_name="Dispatcher Testing",
            email="dispatcher_demo@demo.com",
            password="somestrongpass2022",
        )

        self.dispatcher = Dispatcher.objects.create(organization_name="Dispatcher Testing Inc.")
        self.dispatcher_user = DispatcherUser.objects.create(user=self.user, dispatcher=self.dispatcher)

        Load.objects.create(
            origin={
                "city": "NEW PLYMOUTH",
                "state": "ID",
                "zipcode": "83655",
                "address1": None,
                "address2": None,
                "latitude": 43.96941,
                "longitude": -116.81852,
            },
            destination={
                "city": "HELENA",
                "state": "MT",
                "zipcode": "59626",
                "address1": None,
                "address2": None,
                "latitude": 46.59808,
                "longitude": -112.01884,
            },
            pickup_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            dropoff_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
            current_status="available",
            details={"weight": "345", "commodity": "Soy", "length": "100", "trailer_type": "Van"},
            contact={
                "info": "",
                "phone": "123456789",
                "email": "test@email.com",
                "reference_number": "123984",
                "notes": "",
            },
            posted_rate=Decimal(1000),
            created_by=self.user,
        )

        Load.objects.create(
            origin={
                "city": "NAMPA",
                "state": "ID",
                "zipcode": "83651",
                "address1": None,
                "address2": None,
                "latitude": 43.58246,
                "longitude": -116.56374,
            },
            destination={
                "city": "BUFFALO",
                "state": "NY",
                "zipcode": "14201",
                "address1": None,
                "address2": None,
                "latitude": 42.87941,
                "longitude": -78.87749,
            },
            pickup_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
            dropoff_date=(datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S"),
            current_status="booked",
            details={"weight": "345", "commodity": "Corn", "length": "100", "trailer_type": "Van"},
            contact={
                "info": "",
                "phone": "123456789",
                "email": "test@email.com",
                "reference_number": "123984",
                "notes": "",
            },
            posted_rate=Decimal(2000),
            created_by=self.user,
        )

        Load.objects.create(
            origin={
                "city": "Atlanta",
                "state": "GA",
                "zipcode": "30033",
                "address1": None,
                "address2": None,
                "latitude": 43.58246,
                "longitude": -116.56374,
            },
            destination={
                "city": "IDAHO FALLS",
                "state": "ID",
                "zipcode": "83404",
                "address1": None,
                "address2": None,
                "latitude": 43.49215,
                "longitude": -112.03962,
            },
            pickup_date=(datetime.now() + timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"),
            dropoff_date=(datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
            current_status="available",
            details={"weight": "345", "commodity": "Corn", "length": "100", "trailer_type": "Van"},
            contact={
                "info": "",
                "phone": "123456789",
                "email": "test@email.com",
                "reference_number": "123984",
                "notes": "",
            },
            posted_rate=Decimal(2000),
            created_by=self.user,
        )

        Load.objects.create(
            origin={
                "city": "Marietta",
                "state": "GA",
                "zipcode": "30090",
                "address1": None,
                "address2": None,
                "latitude": 33.9528472,
                "longitude": -116.83404,
            },
            destination={
                "city": "GOODING",
                "state": "ID",
                "zipcode": "83330",
                "address1": None,
                "address2": None,
                "latitude": 42.93879,
                "longitude": -84.5496148,
            },
            pickup_date=(datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            dropoff_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
            current_status="available",
            details={"weight": "345", "commodity": "Corn", "length": "100", "trailer_type": "Van"},
            contact={
                "info": "",
                "phone": "123456789",
                "email": "test@email.com",
                "reference_number": "123984",
                "notes": "",
            },
            posted_rate=Decimal(2000),
            created_by=self.user,
        )

        Load.objects.create(
            origin={
                "city": "Atlanta",
                "state": "GA",
                "zipcode": "30301",
                "address1": None,
                "address2": None,
                "latitude": 33.7489924,
                "longitude": -84.3902644,
            },
            destination={
                "city": "GOODING",
                "state": "ID",
                "zipcode": "83330",
                "address1": None,
                "address2": None,
                "latitude": 42.93879,
                "longitude": -114.7131,
            },
            pickup_date=(datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
            dropoff_date=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
            current_status="available",
            details={"weight": "345", "commodity": "Corn", "length": "100", "trailer_type": "Van"},
            contact={
                "info": "",
                "phone": "123456789",
                "email": "test@email.com",
                "reference_number": "123984",
                "notes": "",
            },
            posted_rate=Decimal(2000),
            created_by=self.user,
        )

        Load.objects.create(
            origin={
                "city": "BUFFALO",
                "state": "NY",
                "zipcode": "14201",
                "address1": None,
                "address2": None,
                "latitude": 42.87941,
                "longitude": -78.87749,
            },
            destination={
                "city": "LOS ANGELES",
                "state": "CA",
                "zipcode": "90012",
                "address1": None,
                "address2": None,
                "latitude": 34.06336,
                "longitude": -118.24905,
            },
            pickup_date=(datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
            dropoff_date=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
            current_status="booked",
            details={"weight": "345", "commodity": "Corn", "length": "100", "trailer_type": "Van"},
            contact={
                "info": "",
                "phone": "123456789",
                "email": "test@email.com",
                "reference_number": "123984",
                "notes": "",
            },
            posted_rate=Decimal(2000),
            created_by=self.user,
        )

    def test_search_all_available(self):
        self.client.force_authenticate(user=self.user)
        query = {}

        response = self.client.get(self.load_url, data=query)
        self.assertEqual(response.data.get("count"), 4)
        self.assertEqual(response.status_code, 200)

    def test_search_pickup_date(self):
        self.client.force_authenticate(user=self.user)
        query = {"pickup_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")}
        response = self.client.get(self.load_url, data=query)
        self.assertEqual(response.data.get("count"), 1)
        self.assertEqual(response.status_code, 200)

    def test_search_dropoff_date(self):
        self.client.force_authenticate(user=self.user)
        query = {"dropoff_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")}
        response = self.client.get(self.load_url, data=query)
        self.assertEqual(response.data.get("count"), 2)
        self.assertEqual(response.status_code, 200)

    def test_search_pickup_and_dropoff_date(self):
        self.client.force_authenticate(user=self.user)
        query = {
            "pickup_date": (datetime.now() + timedelta(days=6)).strftime("%Y-%m-%d"),
            "dropoff_date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
        }
        response = self.client.get(self.load_url, data=query)
        self.assertEqual(response.data.get("count"), 1)
        self.assertEqual(response.status_code, 200)

    def test_search_pickup_load_with_radius(self):
        self.client.force_authenticate(user=self.user)
        query = {
            "pickup": "nampa,id",
            "pickup_radius": 100,
        }
        response = self.client.get(self.load_url, data=query)
        self.assertEqual(response.data.get("count"), 1)
        self.assertEqual(response.status_code, 200)

    def test_search_pickup_without_radius(self):
        self.client.force_authenticate(user=self.user)
        query = {
            "pickup": "atlanta,ga",
        }
        response = self.client.get(self.load_url, data=query)
        self.assertEqual(response.data.get("count"), 2)
        self.assertEqual(response.status_code, 200)

    def test_search_dropoff_with_radius(self):
        self.client.force_authenticate(user=self.user)
        query = {
            "dropoff": "helena,mt",
            "dropoff_radius": 100,
        }
        response = self.client.get(self.load_url, data=query)
        self.assertEqual(response.data.get("count"), 1)
        self.assertEqual(response.status_code, 200)

    def test_search_dropoff_without_radius(self):
        self.client.force_authenticate(user=self.user)
        query = {
            "dropoff": "helena,mt",
        }
        response = self.client.get(self.load_url, data=query)
        self.assertEqual(response.data.get("count"), 1)
        self.assertEqual(response.status_code, 200)

    def test_search_dropoff_load_booked(self):
        self.client.force_authenticate(user=self.user)
        query = {
            "dropoff": "buffalo,ny",
            "dropoff_radius": 100,
        }
        response = self.client.get(self.load_url, data=query)
        self.assertEqual(response.data.get("count"), 0)
        self.assertEqual(response.status_code, 200)

    def test_search_pickup_and_dropoff(self):
        self.client.force_authenticate(user=self.user)
        query = {
            "pickup": "Marietta,ga",
            "pickup_radius": 100,
            "dropoff": "GOODING,id",
            "dropoff_radius": 100,
        }
        response = self.client.get(self.load_url, data=query)
        self.assertEqual(response.data.get("count"), 2)
        self.assertEqual(response.status_code, 200)

    def test_search_distance_local(self):
        self.client.force_authenticate(user=self.user)
        query = {
            "distance": "local",
        }
        response = self.client.get(self.load_url, data=query)
        self.assertEqual(response.data.get("count"), 0)
        self.assertEqual(response.status_code, 200)

    def test_search_distance_medium(self):
        self.client.force_authenticate(user=self.user)
        query = {
            "distance": "medium",
        }
        response = self.client.get(self.load_url, data=query)
        self.assertEqual(response.data.get("count"), 2)
        self.assertEqual(response.status_code, 200)

    def test_search_distance_long(self):
        self.client.force_authenticate(user=self.user)
        query = {
            "distance": "long",
        }
        response = self.client.get(self.load_url, data=query)
        self.assertEqual(response.data.get("count"), 2)
        self.assertEqual(response.status_code, 200)
