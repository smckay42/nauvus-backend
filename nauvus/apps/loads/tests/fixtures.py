import random
import time

import pytest

from nauvus.apps.broker.tests.fixtures import broker
from nauvus.apps.loads.models import Load
from nauvus.utils.helpers import milliseconds_to_datetime


def create_load(faker):
    load = Load()
    NOW = round(time.time()) * 1000
    ONE_DAY = (60 * 60 * 24) * 1000

    # origin_state = faker.state_abbr(False)
    # destination_state = faker.state_abbr(False)
    # origin_city = faker.city()
    # destination_city = faker.city()
    # origin_zip = faker.postcode_in_state(origin_state)
    # destination_zip = faker.postcode_in_state(destination_zip)
    origin_city = "Atlanta"
    destination_city = "Miami"
    origin_state = "GA"
    destination_state = "FL"
    origin_zip = "30342"
    destination_zip = "33140"

    load.origin = {
        "address1": faker.street_address(),
        "city": origin_city,
        "state": origin_state,
        "zipcode": origin_zip,
    }

    load.destination = {
        "address1": faker.street_address(),
        "city": destination_city,
        "state": destination_state,
        "zipcode": destination_zip,
    }

    load.pickup_date = milliseconds_to_datetime(NOW)
    load.dropoff_date = milliseconds_to_datetime(NOW + ONE_DAY * 7)

    load.posted_rate = round(random.uniform(300.00, 4000.00), 2)
    load.current_status = Load.Status.AVAILABLE

    return load


@pytest.fixture
def load(faker, broker):

    load = create_load(faker)
    load.broker = broker
    load.save()

    return load


@pytest.fixture
def load_not_in_db(request, faker):

    load = create_load(faker)
    request.cls.load = load
