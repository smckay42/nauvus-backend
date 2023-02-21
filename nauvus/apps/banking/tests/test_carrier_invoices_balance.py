from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from nauvus.apps.broker.models import Broker
from nauvus.apps.carrier.models import CarrierUser, Carrier
from nauvus.apps.driver.models import Driver, CarrierDriver
from nauvus.apps.loads.models import Load
from nauvus.apps.payments.models import Invoice, LoadSettlement, Loan


class TestCarrierInvoiceBalance(APITestCase):
    def setUp(self) -> None:
        self.url = "/api/v1/banking/carriers-invoices-balance/"

        self.user = get_user_model().objects.create_user(username="carrier_test", first_name="Carrier Testing",
                                                         email="justin@nauvus.com",
                                                         password='somestrongpass2022', user_type='carrier_owner',
                                                         stripe_customer_id="acct_1LuWFND15eBQjeU2")
        self.carrier = Carrier.objects.create(organization_name='Carrier Testing Inc.', street1='Carrier St.',
                                              street2='', city='Atlanta', state='GA', zip_code='987654321')
        self.carrier_user = CarrierUser.objects.create(user=self.user, carrier=self.carrier,
                                                       is_current_organization=True, access_type='full_admin')

        self.user_2 = get_user_model().objects.create_user(username="driver_test", first_name="Driver Testing",
                                                           email="driver_demo@demo.com",
                                                           password='somestrongpass2022', user_type='driver')
        self.driver = Driver.objects.create(user=self.user_2)
        self.driver_carrier = CarrierDriver.objects.create(driver=self.driver, carrier=self.carrier,
                                                           carrier_user=self.carrier_user)

        self.broker = Broker.objects.create(name='Broker Test', phone='+1123456789', email='broker@yopmail.com',
                                            mc_number='123456789', street1='Test St.', city='New York', state='NY',
                                            zip_code='1234567', street2='')

        self.load = Load.objects.create(
            origin={"city": "NAMPA", "state": "ID", "zipcode": "83651", "address1": None, "address2": None,
                    "latitude": 43.58246, "longitude": -116.56374},
            destination={"city": "BUFFALO", "state": "NY", "zipcode": "14201", "address1": None, "address2": None,
                         "latitude": 42.87941, "longitude": -78.87749},
            pickup_date=(datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S"),
            dropoff_date=(datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S"),
            current_status="booked",
            details={"weight": "345", "commodity": "Soy", "length": "100", "trailer_type": "Van"},
            contact={"info": "", "phone": "123456789", "email": "test@email.com", "reference_number": "123984",
                     "notes": ""},
            posted_rate=Decimal(2000),
            driver=self.driver,
            broker=self.broker,
            final_rate=Decimal(1000),
        )

        self.load_2 = Load.objects.create(
            origin={"city": "NEW PLYMOUTH", "state": "ID", "zipcode": "83655", "address1": None, "address2": None,
                    "latitude": 43.96941, "longitude": -116.81852},
            destination={"city": "HELENA", "state": "MT", "zipcode": "59626", "address1": None, "address2": None,
                         "latitude": 46.59808, "longitude": -112.01884},
            pickup_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            dropoff_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
            current_status="available",
            details={"weight": "345", "commodity": "Soy", "length": "100", "trailer_type": "Van"},
            contact={"info": "", "phone": "123456789", "email": "test@email.com", "reference_number": "123984",
                     "notes": ""},
            posted_rate=Decimal(5000),
            created_by=self.user,
            driver=self.driver,
            broker=self.broker,
            final_rate=Decimal(2500),
        )

        self.load_settlement = LoadSettlement.objects.create(load=self.load, nauvus_fee_percent=Decimal(10),
                                                             nauvus_fees_in_cents=10000)

        self.load_settlement_2 = LoadSettlement.objects.create(load=self.load_2, nauvus_fee_percent=Decimal(10),
                                                               nauvus_fees_in_cents=25000)

        self.invoice = Invoice.objects.create(broker=self.broker, carrier_user=self.carrier_user,
                                              amount_due_in_cents=100000, load_settlement=self.load_settlement)

        self.invoice_2 = Invoice.objects.create(broker=self.broker, carrier_user=self.carrier_user,
                                                amount_due_in_cents=250000, load_settlement=self.load_settlement_2)

        self.loan = Loan.objects.create(principal_amount_in_cents=25000, fee_amount_in_cents=5000, invoice=self.invoice)

        self.loan = Loan.objects.create(principal_amount_in_cents=25000, fee_amount_in_cents=5000,
                                        invoice=self.invoice_2)

    def test_user_is_not_carrier_returns_403(self):
        # User 2 is driver
        self.client.force_authenticate(self.user_2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_carrier_get_balance_returns_200(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_carrier_get_balance_total_2550(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.data[2].get('total'), Decimal(2550))
