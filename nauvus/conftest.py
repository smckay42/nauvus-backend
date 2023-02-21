import random
import time

import pytest

from nauvus.apps.broker.tests.fixtures import broker, broker_for_class
from nauvus.apps.carrier.tests.fixtures import carrier, carrier_user
from nauvus.apps.dispatcher.tests.fixtures import dispatcher, dispatcher_user
from nauvus.apps.driver.tests.fixtures import driver
from nauvus.apps.loads.tests.fixtures import load, load_not_in_db
from nauvus.utils.helpers import (
    create_broker,
    create_carrier,
    create_carrier_driver,
    create_carrier_user,
    create_invoice,
    create_load,
    create_load_settlement,
    create_user,
)

NOW = round(time.time()) * 1000
ONE_DAY = (60 * 60 * 24) * 1000


@pytest.fixture(scope="function", autouse=True)
def faker_seed():
    return random.randint(0, 100000000)


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(faker):
    return create_user(faker)


# @pytest.fixture
# def broker(faker):
#     return create_broker(faker)


@pytest.fixture
def available_load(request, load):

    request.cls.load = load


@pytest.fixture
def carrier_user_for_class(request, carrier_user):
    request.cls.carrier_user = carrier_user


@pytest.fixture
def dispatcher_user_for_class(request, dispatcher_user):
    request.cls.dispatcher_user = dispatcher_user


@pytest.fixture
def load_for_testclass(request, faker):
    load = create_load(faker)
    load.broker = create_broker(faker)
    settlement = create_load_settlement(load)
    test_invoice = create_invoice(faker, load.broker, carrier_user=None, paid=False)
    test_invoice.amount_due_in_cents = load.final_rate * 100
    test_invoice.load_settlement = settlement

    request.cls.load_settlement = settlement
    request.cls.invoice = test_invoice
    request.cls.load = load


@pytest.fixture
def underway_load_for_testclass(request, faker):
    load = create_load(faker)
    load.broker = create_broker(faker)

    request.cls.load = load


@pytest.fixture
def carrier_user_for_testclass(request, faker, user, carrier):
    carrier_user = create_carrier_user(user, carrier)
    carrier_driver = create_carrier_driver(faker, carrier)

    request.cls.carrier_user = carrier_user
    request.cls.carrier_driver = carrier_driver


# @pytest.fixture
# def carrier_user(user, carrier):
#     return create_carrier_user(user, carrier)


# @pytest.fixture
# def carrier(faker):
#     return create_carrier(faker)


@pytest.fixture
def invoices(faker, broker, carrier_user):
    test_invoices = []

    for x in range(0, random.randint(8, 13)):
        test_invoices.append(create_invoice(faker, broker, carrier_user, bool(random.getrandbits(1))))

    return test_invoices


@pytest.fixture
def invoice(faker, broker, carrier_user):
    return create_invoice(faker, broker, carrier_user, bool(random.getrandbits(1)))


@pytest.fixture
def paid_invoice(faker, broker, carrier_user):
    return create_invoice(faker, broker, carrier_user, True)


@pytest.fixture
def unpaid_invoice(faker, broker, carrier_user):
    return create_invoice(faker, broker, carrier_user, False)


@pytest.fixture
def load_settlement(load):
    return create_load_settlement(load)


# @pytest.fixture
# def load(faker, broker):
#     load = create_load(faker)
#     load.broker = broker
#     return load
