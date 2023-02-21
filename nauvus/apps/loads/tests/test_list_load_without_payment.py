from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.apps.driver.models import Driver
from nauvus.apps.loads.models import Load
from nauvus.apps.payments.models import LoadSettlement, Invoice, Loan, Payment


class TestListLoadWithoutPayment(APITestCase):

    def setUp(self):
        self.url = "/api/v1/loads/"

        self.user_dispatcher = get_user_model().objects.create_user(
            username="dispatcher_test",
            first_name="Dispatcher Testing",
            email="dispatcher_demo@demo.com",
            password='somestrongpass2022',
        )

        self.dispatcher = Dispatcher.objects.create(organization_name='Dispatcher Testing Inc.')
        self.dispatcher_user = DispatcherUser.objects.create(user=self.user_dispatcher, dispatcher=self.dispatcher)
        self.driver = Driver.objects.create(user=self.user_dispatcher)

        self.load = Load.objects.create(
            origin={"address1": "Test St.", "address2": "Test", "city": "New York", "state": "NY", "longitude": "123",
                    "latitude": "123", "zipcode": "123"},
            destination={"address1": "Test Destination St.", "address2": "Test", "city": "Miami", "state": "FL",
                         "longitude": "321", "latitude": "567", "zipcode": "123478"},
            pickup_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            dropoff_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
            current_status="available",
            details={"weight": "345", "commodity": "Soy", "length": "100", "trailer_type": "Van"},
            contact={"info": "", "phone": "123456789", "email": "test@email.com", "reference_number": "123984",
                     "notes": ""},
            posted_rate=Decimal(100000),
            dispatcher=self.dispatcher_user,
            created_by=self.user_dispatcher,
            driver=self.driver
        )
        self.settlement = LoadSettlement.objects.create(load=self.load, nauvus_fee_percent=Decimal(5),
                                                        nauvus_fees_in_cents=1000)
        self.invoice = Invoice.objects.create(amount_due_in_cents=100000, load_settlement=self.settlement)
        # Loan.objects.create(principal_amount_in_cents=23000, fee_amount_in_cents=1910, invoice=self.invoice)
        # Payment.objects.create(load_settlement=self.settlement, amount_in_cents=40000)
        # Payment.objects.create(load_settlement=self.settlement, amount_in_cents=20000)

        self.client.force_authenticate(user=self.user_dispatcher)

        return super().setUp()

    # @pytest.mark.django_db
    def test_list_loads_returns_status_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_list_user_load_returns_load_content(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data.get('results')[0].get('payment_to_date'), 0.00)
        self.assertEqual(response.data.get('results')[0].get('remain_payment'), 990.0)
