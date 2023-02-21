import pytest
from rest_framework.test import APITestCase

from nauvus.apps.loads.models import Load
from nauvus.utils.helpers import generate_file


@pytest.mark.usefixtures("available_load", "carrier_user_for_class", "dispatcher_user_for_class")
class TestBookLoad(APITestCase):
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
        cls.url_base = "/api/v1/loads"
        cls.rc_document = generate_file("rc_document")
        return super().setUpTestData()

    def setUp(self):
        pass

    @pytest.mark.django_db
    def test_bookload_as_dispatcher(self):
        load_id = str(self.load.id)
        load = Load.objects.get(pk=load_id)

        self.client.force_authenticate(user=self.dispatcher_user.user)

        url = f"{self.url_base}/{load_id}/rate-confirmation/"

        form_data = {"document": self.rc_document}

        response = self.client.post(url, data=form_data, format="multipart")

        self.assertEqual(response.status_code, 201)

        url = f"{self.url_base}/{load_id}/book/"

        response = self.client.put(url, self.get_form_data(), format="json")

        self.assertEqual(response.status_code, 200)

        load.refresh_from_db()

        self.assertEqual(load.current_status, Load.Status.BOOKED)

    @pytest.mark.django_db
    def test_bookload_as_carrier(self):
        load_id = str(self.load.id)
        load = Load.objects.get(pk=load_id)

        self.client.force_authenticate(user=self.carrier_user.user)

        url = f"{self.url_base}/{load_id}/rate-confirmation/"

        form_data = {"document": self.rc_document}

        response = self.client.post(url, data=form_data, format="multipart")

        self.assertEqual(response.status_code, 201)

        url = f"{self.url_base}/{load_id}/book/"

        response = self.client.put(url, self.get_form_data(), format="json")

        self.assertEqual(response.status_code, 200)

        load.refresh_from_db()

        self.assertEqual(load.current_status, Load.Status.BOOKED)

    @pytest.mark.django_db
    def test_add_and_delete_rc_document_as_carrier(self):
        load_id = str(self.load.id)
        load = Load.objects.get(pk=load_id)

        self.client.force_authenticate(user=self.carrier_user.user)

        url = f"{self.url_base}/{load_id}/rate-confirmation/"

        form_data = {"document": self.rc_document}

        response = self.client.post(url, data=form_data, format="multipart")

        self.assertEqual(response.status_code, 201)

        load.refresh_from_db()

        self.assertIsNotNone(load.rc_document.name)

        response = self.client.delete(url)

        self.assertEquals(response.status_code, 200)

        load.refresh_from_db()

        self.assertEquals(load.rc_document.name, "")
