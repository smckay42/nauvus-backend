from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.broker.models import Broker
from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.apps.loads.models import Load, LoadSource


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

        # Necessary to update load_id with a current load available on 123Loadboard
        self.load_source = LoadSource.objects.create(load_id='371ae47f-115d-44c5-b5bb-2aaf73dd29ca',
                                                     source='LOADBOARD_123')

        self.broker = Broker.objects.create(external_broker_id='18ad47a2-7693-4154-8b02-a2bc57696a9b',
                                            name='Royal Transportation Services', mc_number='698365', metadata={})

        self.load = Load.objects.create(
            source=self.load_source,
            broker=self.broker,
            origin={"address1": "Test St.", "address2": "Test", "city": "New York", "state": "NY", "longitude": "123",
                    "latitude": "123", "zipcode": "123"},
            destination={"address1": "Test Destination St.", "address2": "Test", "city": "Miami", "state": "FL",
                         "longitude": "321", "latitude": "567", "zipcode": "123478"},
            pickup_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            dropoff_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
            current_status="available",
            details={"weight": "345", "commodity": "Soy", "length": "100", "trailer_type": "Van"},
            contact={"info": "", "phone": "", "email": "", "reference_number": "",
                     "notes": ""}, posted_rate=Decimal(1000),
        )

    def test_get_load_details_returns_200(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        response = self.client.get(f"{self.load_url}{self.load.id}/")
        self.assertEqual(response.status_code, 200)

    def test_get_load_detail_check_response(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        response = self.client.get(f"{self.load_url}{self.load.id}/")
        data = response.json()
        self.assertEqual(data.get('data').get('posted_rate'), "1000.00")
