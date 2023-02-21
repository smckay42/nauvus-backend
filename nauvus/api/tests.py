from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Seeds initial test data common for multiple tests."""
        settings.ACCOUNT_EMAIL_VERIFICATION = (
            "optional"  # set email verification optinal only for testcases
        )

        call_command("loaddata", "group", "-v", "0")

    def setUp(self):
        """Instantiate clients and create test scoped objects."""
        # settings.ACCOUNT_EMAIL_VERIFICATION = (
        #     "optional"  # set email verification optinal only for testcases
        # )
        self.faker = Faker()
        self.client = APIClient()

    def login_account_admin_user(self):
        def request(client, data):
            return client.post(reverse("api:auth:user_login"), data=data, format="json")

        self.userrole = "Admin"
        self.username = "admintest"
        self.password = "unittest"
        self.email = "admin.test@demo.com"

        # create user
        self.user = get_user_model().objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
        )

        # set group to user
        group = Group.objects.get(name=self.userrole)
        group.user_set.add(self.user)

        data = {"email": self.email, "password": self.password}
        response = request(self.client, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.authorization_token = "JWT " + response.data["token"]
