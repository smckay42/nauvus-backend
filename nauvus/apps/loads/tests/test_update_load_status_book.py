import json
import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.apps.loads.models import Load


class TestUpdateLoadStatusBookAPI(APITestCase):

    def setUp(self):
        self.load_url = "/api/v1/loads"

        self.user_dispatcher = get_user_model().objects.create_user(username="dispatcher_test",
                                                                    first_name="Dispatcher Testing",
                                                                    email="dispatcher_demo@demo.com",
                                                                    password='somestrongpass2022')
        self.dispatcher = Dispatcher.objects.create(organization_name='Dispatcher Testing Inc.')
        self.dispatcher_user = DispatcherUser.objects.create(user=self.user_dispatcher, dispatcher=self.dispatcher)

        self.user_dispatcher_2 = get_user_model().objects.create_user(username="another_dispatcher",
                                                                      first_name="Anohter Dispatcher Testing",
                                                                      email="dispatcher_another@demo.com",
                                                                      password='somestrongpass2022')
        self.dispatcher_2 = Dispatcher.objects.create(organization_name='Dispatcher Another Inc.')
        self.dispatcher_user_2 = DispatcherUser.objects.create(user=self.user_dispatcher_2,
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
                     "notes": ""}, posted_rate=Decimal(1000),
            dispatcher=self.dispatcher_user,
            created_by=self.user_dispatcher
        )

    @unittest.skip
    def test_update_load_status_missing_parameters_code_400(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        response = self.client.post(f"{self.load_url}/{self.load.id}/test/")
        self.assertEqual(response.status_code, 400)

    @unittest.skip
    def test_update_load_status_book(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        response = self.client.post(f"{self.load_url}/{self.load.id}/book/")
        status_updated = json.loads(response.content).get('data').get('current_status')
        self.assertEqual(status_updated, 'booked')

    @unittest.skip
    def test_update_load_status_accept(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        response = self.client.post(f"{self.load_url}/{self.load.id}/accept/")
        status_updated = json.loads(response.content).get('data').get('current_status')
        self.assertEqual(status_updated, 'upcoming')

    @unittest.skip
    def test_update_load_status_reject(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        response = self.client.post(f"{self.load_url}/{self.load.id}/reject/")
        status_updated = json.loads(response.content).get('data').get('current_status')
        self.assertEqual(status_updated, 'booked')

    @unittest.skip
    def test_update_load_status_start(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        response = self.client.post(f"{self.load_url}/{self.load.id}/start/")
        status_updated = json.loads(response.content).get('data').get('current_status')
        self.assertEqual(status_updated, 'underway')

    @unittest.skip
    def test_update_load_status_deliver(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        response = self.client.post(f"{self.load_url}/{self.load.id}/deliver/")
        status_updated = json.loads(response.content).get('data').get('current_status')
        self.assertEqual(status_updated, 'delivered')
