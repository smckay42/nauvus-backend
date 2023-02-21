from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from config import settings
from nauvus.apps.carrier.models import CarrierUser
from nauvus.apps.dispatcher.models import DispatcherUser, Dispatcher, DispatcherServiceAgreement
from nauvus.services.docusign.docusign import docusign_worker


class TestDocusignWorker(TestCase):
    def setUp(self):
        settings.ACCOUNT_EMAIL_VERIFICATION = (
            "optional"  # set email verification optinal only for testcases
        )

        self.client = Client()

        self.user_carrier = get_user_model().objects.create_user(
            username="carrier_test",
            first_name="Carrier Testing",
            # Please, enter a valid email to receive the documentation from Docusign
            email="carrier_demo@demo.com",
            password='somestrongpass2022',
        )
        self.carrier = CarrierUser.objects.create(user=self.user_carrier)

        self.user_dispatcher = get_user_model().objects.create_user(
            username="dispatcher_test",
            first_name="Dispatcher Testing",

            # Please, enter a valid email to receive the documentation from Docusign
            email="dispatcher_demo@demo.com",

            password='somestrongpass2022',
        )

        self.dispatcher = Dispatcher.objects.create(organization_name='Dispatcher Testing Inc.')
        self.dispatcher_user = DispatcherUser.objects.create(user=self.user_dispatcher, dispatcher=self.dispatcher)


    def test_send_doc_to_carrier_return_ok(self):
        result = docusign_worker(self.user_carrier)
        self.assertIn('envelope_id', result.keys())

    def test_send_doc_to_dispatcher_return_ok(self):
        result = docusign_worker(self.user_dispatcher)
        self.assertIn('envelope_id', result.keys())
