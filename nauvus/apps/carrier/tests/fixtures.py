import random

import pytest

from nauvus.apps.carrier.models import Carrier, CarrierUser
from nauvus.apps.driver.models import CarrierDriver
from nauvus.users.models import User
from nauvus.utils.helpers import create_user


@pytest.fixture
def carrier_user(faker, carrier):
    user = create_user(faker)
    user.user_type = User.CARRIER_OWNER
    user.stripe_customer_id = "acct_1Lu1pBBdeZ77yAv7"
    user.save()

    cu = CarrierUser.objects.create(user=user, carrier=carrier)
    return cu


@pytest.fixture
def carrier(faker, driver):
    state = faker.state_abbr(False)
    zip_code = faker.postcode_in_state(state)

    carrier = Carrier.objects.create(
        organization_name=f"{faker.company()} Carriers",
        mc_number=str(random.randint(1000000, 9999999)),
        street1=faker.street_address(),
        city=faker.city(),
        state=state,
        zip_code=zip_code,
    )

    CarrierDriver.objects.create(driver=driver, carrier=carrier)

    return carrier
