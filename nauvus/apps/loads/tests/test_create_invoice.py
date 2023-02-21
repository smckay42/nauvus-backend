import io
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from PIL import Image
from rest_framework.test import APITestCase

from nauvus.apps.broker.models import Broker
from nauvus.apps.carrier.models import Carrier, CarrierUser
from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.apps.driver.models import CarrierDriver, Driver
from nauvus.apps.loads.models import Load


class TestCreateCompleteDeliveryDocumentCAndCreateAndSendInvoice(APITestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/loads/complete-delivery-documents/"

        self.user = get_user_model().objects.create_user(
            username="carrier_test",
            first_name="Carrier Testing",
            email="justin@nauvus.com",
            password="somestrongpass2022",
            user_type="carrier_owner",
            stripe_customer_id="acct_1Lu1pBBdeZ77yAv7",
        )
        self.carrier = Carrier.objects.create(
            organization_name="Carrier Testing Inc.",
            street1="Carrier St.",
            street2="",
            city="Atlanta",
            state="GA",
            zip_code="987654321",
        )
        self.carrier_user = CarrierUser.objects.create(
            user=self.user, carrier=self.carrier, is_current_organization=True, access_type="full_admin"
        )

        self.broker = Broker.objects.create(
            name="Broker Test",
            phone="+1123456789",
            email="broker@yopmail.com",
            mc_number="123456789",
            street1="Test St.",
            city="New York",
            state="NY",
            zip_code="1234567",
            street2="",
        )

        self.user_2 = get_user_model().objects.create_user(
            username="driver_test",
            first_name="Driver Testing",
            email="driver_demo@demo.com",
            password="somestrongpass2022",
            user_type="driver",
        )
        self.driver = Driver.objects.create(user=self.user_2)
        self.driver_carrier = CarrierDriver.objects.create(
            driver=self.driver, carrier=self.carrier, carrier_user=self.carrier_user
        )

        self.user_3 = get_user_model().objects.create_user(
            username="dispatcher_test",
            first_name="Disaptcher Testing",
            email="dispatcher@demo.com",
            password="somestrongpass2022",
            user_type="dispatcher",
        )
        self.dispatcher = Dispatcher.objects.create(organization_name="Dispatcher Testing Inc.")
        self.dispatcher_user = DispatcherUser.objects.create(user=self.user_3, dispatcher=self.dispatcher)

        self.load = Load.objects.create(
            origin={
                "city": "NAMPA",
                "state": "ID",
                "zipcode": "83651",
                "address1": None,
                "address2": None,
                "latitude": 43.58246,
                "longitude": -116.56374,
            },
            destination={
                "city": "BUFFALO",
                "state": "NY",
                "zipcode": "14201",
                "address1": None,
                "address2": None,
                "latitude": 42.87941,
                "longitude": -78.87749,
            },
            pickup_date=(datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S"),
            dropoff_date=(datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S"),
            current_status="booked",
            details={"weight": "345", "commodity": "Soy", "length": "100", "trailer_type": "Van"},
            contact={
                "info": "",
                "phone": "123456789",
                "email": "test@email.com",
                "reference_number": "123984",
                "notes": "",
            },
            posted_rate=Decimal(2000),
            driver=self.driver,
            broker=self.broker,
            final_rate=Decimal(2.30),
        )

    def generate_file(self, file_name):
        file = io.BytesIO()
        image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
        image.save(file, "png")
        file.name = f"{file_name}.png"
        file.seek(0)
        return file
