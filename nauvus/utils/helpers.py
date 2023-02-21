import datetime
import io
import random
import time

from django.conf import settings
from django.contrib.auth import get_user_model
from PIL import Image

from nauvus.apps.broker.models import Broker
from nauvus.apps.carrier.models import Carrier, CarrierUser
from nauvus.apps.driver.models import CarrierDriver, Driver
from nauvus.apps.loads.models import Load
from nauvus.apps.payments.models import Invoice, LoadSettlement, Loan, Payment
from nauvus.users.models import User

NOW = round(time.time()) * 1000
ONE_DAY = (60 * 60 * 24) * 1000


def milliseconds_to_datetime(ms_since_epoch):
    return datetime.datetime.utcfromtimestamp(ms_since_epoch / 1000).replace(tzinfo=datetime.timezone.utc)


def generate_otp(phone):
    """Generating the otp"""
    if phone:
        key = random.randint(999, 9999)
        return key
    else:
        return False


def create_email(first, last, company):
    email_address = (
        first.lower() + "." + last.lower() + "@" + company.lower().replace(" ", "").replace(",", "") + ".com"
    )
    return email_address


def create_user(faker):
    first_name = faker.first_name()
    last_name = faker.last_name()
    email = create_email(first_name, last_name, faker.company())
    phone = "+1" + str(random.randint(200000000, 9999999999))
    username = first_name + last_name
    user = get_user_model().objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        password=faker.password(),
    )

    return user


def create_broker(faker):
    test_broker = Broker()
    # test_broker.uid = str(uuid.uuid4())  # randomly generated uid
    test_broker.name = f"{faker.company()} {faker.company_suffix()}"
    test_broker.phone = "+1" + str(random.randint(200000000, 9999999999))
    test_broker.mc_number = str(random.randint(1000000, 9999999))
    test_broker.contact_first_name = faker.first_name()
    test_broker.contact_last_name = faker.last_name()
    test_broker.email = (
        test_broker.contact_first_name.lower() + "@" + test_broker.name.lower().replace(" ", "") + ".com"
    )
    test_broker.street1 = faker.street_address()
    test_broker.city = faker.city()
    test_broker.state = faker.state_abbr(False)
    test_broker.zip_code = faker.postcode_in_state(test_broker.state)

    return test_broker


def create_carrier(faker):
    test_carrier = Carrier()
    # test_carrier.pk = random.randint(1000, 10000)
    test_carrier.organization_name = f"{faker.company()} Carriers"
    # test_carrier.uid = str(uuid.uuid4())
    test_carrier.mc_number = str(random.randint(1000000, 9999999))
    test_carrier.street1 = faker.street_address()
    test_carrier.city = faker.city()
    test_carrier.state = faker.state_abbr(False)
    test_carrier.zip_code = faker.postcode_in_state(test_carrier.state)

    return test_carrier


def create_invoice(faker, broker, carrier_user, paid):
    # current time in milliseconds
    invoice = Invoice()

    invoice.amount_due_in_cents = random.randint(30000, 500000)
    invoice.description = faker.bs()
    # invoice.uid = str(uuid.uuid4())

    # add fields to make this an invoice paid in the past
    if paid:
        invoice_date = NOW - (random.randint(7, 30) * ONE_DAY)
        due_date = invoice_date + (3 * ONE_DAY)
        payment_date = due_date  # always pay on due date
        invoice.paid_date = milliseconds_to_datetime(payment_date).date()

    else:
        # this is an unpaid invoice
        invoice_date = NOW - (random.randint(1, 7) * ONE_DAY)
        due_date = invoice_date + (30 * ONE_DAY)

    invoice.due_date = milliseconds_to_datetime(due_date).date()
    invoice.created_at = milliseconds_to_datetime(invoice_date).date()

    invoice.broker = broker
    invoice.carrier_user = carrier_user

    return invoice


def create_carrier_user(user, carrier):
    carrier_user = CarrierUser()

    user.user_type = User.CARRIER_OWNER

    # test account tied to justin@nauvus.com
    user.stripe_customer_id = "acct_1Lu1pBBdeZ77yAv7"
    carrier_user.user = user

    carrier_user.carrier = carrier

    return carrier_user


def create_load(faker):
    load = Load()
    origin_state = faker.state_abbr(False)
    destination_state = faker.state_abbr(False)
    load.origin = {
        "address1": faker.street_address(),
        "city": faker.city(),
        "state": origin_state,
        "zipcode": faker.postcode_in_state(origin_state),
    }

    load.destination = {
        "address1": faker.street_address(),
        "city": faker.city(),
        "state": origin_state,
        "zipcode": faker.postcode_in_state(destination_state),
    }

    load.pickup_date = milliseconds_to_datetime(NOW)
    load.dropoff_date = milliseconds_to_datetime(NOW + ONE_DAY * 7)

    load.posted_rate = round(random.uniform(300.00, 4000.00), 2)
    load.final_rate = load.posted_rate

    return load


def create_driver(faker):
    user = create_user(faker)
    user.user_type = User.DRIVER

    driver = Driver()
    driver.user = user

    return driver


def create_carrier_driver(faker, carrier):
    driver = create_driver(faker)
    carrier_driver = CarrierDriver()
    carrier_driver.driver = driver
    carrier_driver.carrier = carrier
    return carrier_driver


def create_load_settlement(load):
    settlement = LoadSettlement()
    settlement.load = load
    settlement.nauvus_fee_percent = settings.NAUVUS_HANDLING_FEE_PERCENT
    settlement.nauvus_fees_in_cents = round(load.final_rate * 100 * (settlement.nauvus_fee_percent / 100))

    return settlement


def create_loan(load, invoice):
    loan = Loan()
    loan.invoice = invoice
    loan.fee_amount_in_cents = round((load.final_rate * 100) * 0.1)
    loan.principal_amount_in_cents = round(load.final_rate * 100)
    return loan


def create_payment(load_settlement, load):
    payment = Payment()
    payment.load_settlement = load_settlement
    payment.amount_in_cents = round(load.final_rate * 100)
    return payment


def generate_file(file_name):
    file = io.BytesIO()
    image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
    image.save(file, "png")
    file.name = f"{file_name}.png"
    file.seek(0)
    return file
