from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.broker.models import Broker
from nauvus.apps.carrier.models import CarrierUser, Carrier
from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.apps.driver.models import Driver, CarrierDriver
from nauvus.apps.loads.models import Load


class TestCreateLoadAPI(APITestCase):

    def setUp(self):
        self.load_url = "/api/v1/loads/"

        self.user = get_user_model().objects.create_user(username="carrier_test", first_name="Carrier Testing",
                                                         email="justin@nauvus.com",
                                                         password='somestrongpass2022', user_type='carrier_owner',
                                                         stripe_customer_id="acct_1Lu1pBBdeZ77yAv7")
        self.carrier = Carrier.objects.create(organization_name='Carrier Testing Inc.', street1='Carrier St.',
                                              street2='', city='Atlanta', state='GA', zip_code='987654321')
        self.carrier_user = CarrierUser.objects.create(user=self.user, carrier=self.carrier,
                                                       is_current_organization=True, access_type='full_admin')

        # self.broker = Broker.objects.create(name='Broker Test', phone='+1123456789', email='broker@yopmail.com',
        #                                     mc_number='123456789', street1='Test St.', city='New York', state='NY',
        #                                     zip_code='1234567', street2='test')

        self.user_2 = get_user_model().objects.create_user(username="driver_test", first_name="Driver Testing",
                                                           email="driver_demo@demo.com",
                                                           password='somestrongpass2022', user_type='driver')
        self.driver = Driver.objects.create(user=self.user_2)
        self.driver_carrier = CarrierDriver.objects.create(driver=self.driver, carrier=self.carrier,
                                                           carrier_user=self.carrier_user)

        self.user_3 = get_user_model().objects.create_user(username="dispatcher_test", first_name="Disaptcher Testing",
                                                           email="dispatcher@demo.com", password='somestrongpass2022',
                                                           user_type='dispatcher')
        self.dispatcher = Dispatcher.objects.create(organization_name='Dispatcher Testing Inc.')
        self.dispatcher_user = DispatcherUser.objects.create(user=self.user_3, dispatcher=self.dispatcher)

        self.expected_json = {
            "origin": {"address1": "Test St.", "address2": "Test", "city": "New York", "state": "NY", "zipcode": "123"},
            "destination": {"address1": "Test Destination St.", "address2": "Test", "city": "Miami", "state": "FL",
                            "zipcode": "123478"},
            "pickup_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dropoff_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
            "current_status": "available",
            "details": {"weight": "345", "commodity": "Soy", "length": "100", "trailer_type": "Van"},
            "contact": {"info": "", "phone": "123456789", "email": "test@email.com", "reference_number": "123984",
                        "notes": ""},
            "posted_rate": Decimal(1000),
            "broker_name": "LOGISTICS FREIGHTWAYS LLC",
            "broker_mc_number": "491800",
            "broker_email": "broker@mail.com",
            "broker_phone": "+12345678790",
            "broker_contact_first_name": "Jim",
            "broker_contact_last_name": "Harper",
        }

    def test_create_load_unauthenticate_user_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.load_url, data=self.expected_json, format="json")
        self.assertEqual(response.status_code, 401)

    def test_create_load_returns_201(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.load_url, data=self.expected_json, format="json")
        self.assertEqual(response.status_code, 201)

    def test_create_load_check_database(self):
        self.client.force_authenticate(user=self.user_3)
        response = self.client.post(self.load_url, data=self.expected_json, format="json")
        load_saved = Load.objects.all()
        self.assertEqual(load_saved.count(), 1)
        self.assertEqual(load_saved.values_list('broker__name', flat=True)[0], 'LOGISTICS FREIGHTWAYS LLC')
