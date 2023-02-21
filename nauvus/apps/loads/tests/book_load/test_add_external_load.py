import pytest
from rest_framework.test import APITestCase

from nauvus.apps.loads.models import Load
from nauvus.utils.helpers import generate_file


@pytest.mark.usefixtures("carrier_user_for_class", "dispatcher_user_for_class", "load_not_in_db", "broker_for_class")
class TestAddExternalLoad(APITestCase):
    def get_form_data(self):
        carrierdriver = self.carrier_user.carrier.carrierdriver_set.first()

        origin = self.load.origin
        origin["contact"] = {"name": "Pickup Contact ", "phone": "", "email": "bill@nauvus.com", "notes": ""}
        destination = self.load.destination
        destination["contact"] = {"name": "Drop Off Contact ", "phone": "+1234x1", "email": "", "notes": ""}

        form_data = {
            "origin": origin,
            "destination": destination,
            "pickup_date": self.load.pickup_date.strftime("%Y-%m-%d %H:%M:%S"),
            "dropoff_date": self.load.dropoff_date.strftime("%Y-%m-%d %H:%M:%S"),
            "driver": carrierdriver.driver.id,
            "details": {"weight": "", "commodity": "", "length": "", "trailer_type": ""},
            "contact": {"name": "Bill ", "phone": "", "email": "bill@nauvus.com", "notes": ""},
            "final_rate": self.load.posted_rate,
            "reference_title": "test",
            "invoice_email": "justin+broker@nauvus.com",
        }

        return form_data

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url_base = "/api/v1"
        cls.rc_document = generate_file("rc_document")
        return super().setUpTestData()

    def setUp(self):

        pass

    @pytest.mark.django_db
    def test_add_external_load(self):

        self.client.force_authenticate(user=self.dispatcher_user.user)

        url = f"{self.url_base}/broker/"

        # first add a broker
        form_data = {
            "name": self.broker.name,
            "phone": self.broker.phone,
            "mc_number": self.broker.mc_number,
            "email": self.broker.email,
        }

        response = self.client.post(url, data=form_data, format="json")

        self.assertEqual(response.status_code, 201)

        broker_id = response.data["id"]

        url = f"{self.url_base}/loads/"

        form_data = {
            "final_rate": self.load.posted_rate,
            "invoice_email": "justin+broker@nauvus.com",
            "broker": broker_id,
            "rc_document": self.rc_document,
        }

        response = self.client.post(url, data=form_data, format="multipart")

        self.assertEqual(response.status_code, 201)

        load_id = response.data["id"]
        load = Load.objects.get(pk=load_id)

        self.assertEqual(load.current_status, Load.Status.DRAFT)

        url = f"{url}{load_id}/book/"

        response = self.client.put(url, self.get_form_data(), format="json")

        self.assertEqual(response.status_code, 200)

        load.refresh_from_db()

        self.assertEqual(load.current_status, Load.Status.BOOKED)
