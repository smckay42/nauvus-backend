import uuid

from django.conf import settings
from rest_framework.test import APITestCase
from django.test.utils import override_settings

from nauvus.users.models import SignUpOtpVerification
from nauvus.users.models import User



class RestAuthTestCase(APITestCase):
    def setUp(self):
        """Instantiate clients and create test scoped objects."""
        settings.ACCOUNT_EMAIL_VERIFICATION = (
            "optional"  # set email verification optinal only for testcases
        )

        SignUpOtpVerification.objects.create(phone="11111111111", otp="123456",
                                             signup_process_id=uuid.uuid4(), verified=True)

        self.signup_process_id = SignUpOtpVerification.objects.filter(phone="11111111111")[0].signup_process_id

    def test_carrier_register(self):
        """
        It should register new user
        """

        signup_url = '/api/v1/auth/signup/carrier/'

        data = {
            "first_name": "john",
            "last_name": "carrier",
            "username": "carrier_test",
            "email": "julio@nauvus.com",
            "password": "unittest",
            "address": {"street1": "7", "street2": "watson", "city": "aus", "state": "aus", "zip_code": "123456",
                        "permenent_address": False},
            "carrier": {"organization_name": "test carrier company 6", "source": "other", "no_of_trucks": 2,
                        "no_of_trailers": 3, "factoring_company_name": "clark Company", "gross_weekly_revenue": None,
                        "mc_number": "123654", "dot_number": "954632"},
            "signup_process_id": self.signup_process_id,
            "trailer_type": ["dry_van", "flatbed"],
            "trailer_size": ["40_feet", "45_feet"],
        }

        response = self.client.post(signup_url, data=data, format='json')
        self.assertIsNotNone(User.objects.all()[0].stripe_customer_id)
        self.assertEqual(response.status_code, 200)
