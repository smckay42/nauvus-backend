import json
import tempfile

import stripe
from PIL import Image
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from config import settings
from nauvus.apps.dispatcher.models import DispatcherUser, Dispatcher, DispatcherServiceAgreement
from nauvus.users.models import Address


class TestStripeAccountCreate(APITestCase):
    def setUp(self):
        settings.ACCOUNT_EMAIL_VERIFICATION = (
            "optional"
        )

        self.user_dispatcher = get_user_model().objects.create_user(
            username="dispatcher_test",
            first_name="Dispatcher Testing",
            user_type='dispatcher',
            email="dispatcher_demo@demo.com",
            password='somestrongpass2022',
        )

        self.user_address = Address.objects.create(
            user=self.user_dispatcher,
            street1='Testing St.',
            city='New York',
            state='NY',
            zip_code='18400'
        )

        self.dispatcher = Dispatcher.objects.create(organization_name='Dispatcher Testing Inc.')
        self.dispatcher_user = DispatcherUser.objects.create(user=self.user_dispatcher, dispatcher=self.dispatcher,
                                                             is_owner=True)
        DispatcherServiceAgreement.objects.create(dispatcher=self.dispatcher, envelope_id='123456', is_signed=False)

        # super().setUp()
        self.tmp_file = tempfile.NamedTemporaryFile(suffix='.jpeg')
        image = Image.new('RGB', (100, 100))
        image.save(self.tmp_file.name)

        self.payload = {
            "business_type": "company",
            "business_profile_name": "Dispatcher Testing Inc.",
            "business_profile_mcc": "4111",
            "account_number": "000123456789",
            "routing_number": "110000000",
            "id_number": "54321",
            "person_email": "testing@email.com",
            "day": 12,
            "month": 3,
            "year": 1980,
            "person_address_line1": "Testing St.",
            "person_address_line2": "",
            "person_address_city": "New York",
            "person_address_state": "NY",
            "person_address_country": "US",
            "person_address_postal_code": "18400",
            "phone": "+19794293446",
            "identity_document": self.tmp_file
        }

    def test_create_connect_account(self):
        self.client.force_authenticate(user=self.user_dispatcher)
        response = self.client.post('/api/v1/users/account/', self.payload)
        response_data = json.loads(response.content)
        message = response_data['data']['message']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message, 'Account created successfully.')
        self.created_account_id = response_data['data']['account_id']

    def tearDown(self) -> None:
        try:
            stripe.Account.delete(self.created_account_id)
        except AttributeError:
            pass
