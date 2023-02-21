import pytest
from rest_framework.test import APITestCase


@pytest.mark.usefixtures(
    "broker_for_class",
    "carrier_user_for_class",
)
class TestBroker(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.url_base = "/api/v1/broker"
        return super().setUpTestData()

    def setUp(self):
        self.client.force_authenticate(user=self.carrier_user.user)

    @pytest.mark.django_db
    def test_create_broker(self):
        url = f"{self.url_base}/"

        form_data = {
            "name": self.broker.name,
            "phone": self.broker.phone,
            "mc_number": self.broker.mc_number,
            "email": self.broker.email,
        }

        response = self.client.post(url, data=form_data, format="json")

        self.assertEqual(response.status_code, 201)
