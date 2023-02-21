from datetime import datetime

import pytest
from rest_framework.test import APITestCase

from nauvus.apps.loads.models import Load
from nauvus.services.credit.oatfi.api import Oatfi
from nauvus.utils.helpers import generate_file

oatfi_client = Oatfi()


@pytest.mark.usefixtures("underway_load_for_testclass", "carrier_user_for_testclass")
class TestDeliverLoad(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.url_base = "/api/v1/loads"
        return super().setUpTestData()

    def setUp(self) -> None:

        # saving the broker and the carrier will ensure they are already in Oatfi
        self.carrier_user.user.save()
        self.carrier_user.carrier.save()
        self.carrier_user.save()
        self.carrier_driver.driver.user.save()
        self.carrier_driver.driver.save()
        self.carrier_driver.save()
        self.load.broker.save()
        self.load.current_status = Load.Status.UNDERWAY
        self.load.driver = self.carrier_driver.driver
        rc_document = generate_file("rc_document")
        self.load.rc_document.save("rc_document", rc_document)

        self.load.save()

        oatfi_client.save_carrier(self.carrier_user)

        # use the driver as the user
        self.client.force_authenticate(user=self.carrier_driver.driver.user)

        file_1 = generate_file("file_1")
        file_2 = generate_file("file_2")

        self.document_1 = {
            "document": file_1,
            "document_type": "bill_of_lading",
            "notes": "This is a test note",
        }

        self.document_2 = {
            "document": file_2,
            "document_type": "other",
        }

        return super().setUp()

    @pytest.mark.django_db
    def test_get_carrier(self):
        carrier = self.load.get_carrier()
        self.assertEqual(carrier.id, self.carrier_user.carrier_id)

    @pytest.mark.django_db
    def test_deliver_load(self):
        load_id = str(self.load.id)
        url = f"{self.url_base}/{load_id}/delivery-documents/"

        response = self.client.post(url, data=self.document_1, format="multipart")

        self.assertEqual(response.status_code, 201)

        response = self.client.post(url, data=self.document_2, format="multipart")

        self.assertEqual(response.status_code, 201)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data.get("data")), 2, f"Expect 2 files but got {len(data.get('data'))}")

        # now that we have delivery documents, let's test the delivery
        delivery_url = f"{self.url_base}/{load_id}/deliver/"

        delivered_date = datetime.now()
        form_data = {
            "delivered_date": delivered_date.strftime("%Y-%m-%d %H:%M:%S"),
        }

        response = self.client.put(delivery_url, form_data)

        self.assertEqual(response.status_code, 200)

        db_load = Load.objects.get(pk=load_id)
        self.assertEqual(db_load.current_status, Load.Status.DELIVERED)
        self.assertEqual(
            db_load.delivered_date.strftime("%Y-%m-%d %H:%M:%S"), delivered_date.strftime("%Y-%m-%d %H:%M:%S")
        )

    @pytest.mark.django_db
    def test_delete_deliver_document(self):
        load_id = str(self.load.id)
        url = f"{self.url_base}/{load_id}/delivery-documents/"

        response = self.client.post(url, data=self.document_1, format="multipart")

        self.assertEqual(response.status_code, 201)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        doc_info = data.get("data")
        self.assertEqual(len(doc_info), 1, f"Expect one file but got {len(data.get('data'))}")

        doc_id = doc_info[0].get("id")

        response = self.client.delete(url, data={"document_id": doc_id})

        self.assertEqual(response.status_code, 200)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        doc_info = data.get("data")
        self.assertEqual(len(doc_info), 0, f"Expect zero file but got {len(data.get('data'))}")
