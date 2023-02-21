import random

import pytest

from nauvus.apps.broker.models import Broker


@pytest.fixture
def broker(faker):
    name = f"{faker.company()} {faker.company_suffix()}"
    phone = "+1" + str(random.randint(200000000, 9999999999))
    mc_number = str(random.randint(1000000, 9999999))
    contact_first_name = faker.first_name()
    contact_last_name = faker.last_name()
    email = contact_first_name.lower() + "@" + name.lower().replace(" ", "").replace(",", "") + ".com"
    street1 = faker.street_address()
    city = faker.city()
    state = faker.state_abbr(False)
    zip_code = faker.postcode_in_state(state)

    test_broker = Broker.objects.create(
        name=name,
        phone=phone,
        mc_number=mc_number,
        contact_first_name=contact_first_name,
        contact_last_name=contact_last_name,
        email=email,
        street1=street1,
        city=city,
        state=state,
        zip_code=zip_code,
    )

    return test_broker


@pytest.fixture
def broker_for_class(request, broker):
    request.cls.broker = broker
