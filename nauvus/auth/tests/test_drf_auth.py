import unittest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from rest_framework import status

from nauvus.api.tests import BaseTestCase


class RestAuthTestCase(BaseTestCase):
    def setUp(self):
        """Instantiate clients and create test scoped objects."""
        settings.ACCOUNT_EMAIL_VERIFICATION = (
            "optional"  # set email verification optinal only for testcases
        )

        self.client = Client()

        self.username = "unittest"
        self.password = "unittest"
        self.user = get_user_model().objects.create_user(
            username="unittest",
            email="unit.test@demo.com",
            password=self.password,
        )

    def test_register(self):
        """
        It should register new user
        """

        def request(client, data):
            return client.post(
                reverse("api:auth:user_signup"),
                data=data,
                content_type="application/json",
            )

        data = {
            "username": "reunittest",
            "email": "reunit.test@demo.com",
            "password1": "unittest",
            "password2": "unittest",
        }
        response = request(self.client, data)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    @unittest.skip("")
    def test_login(self):
        """
        It should login with already registered user
        """

        def request(client, data):
            return client.post(
                reverse("api:auth:user_login"),
                data=data,
                content_type="application/json",
            )

        data = {"email": self.email, "password": self.password}
        response = request(self.client, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIsNotNone(response.data["token"])
