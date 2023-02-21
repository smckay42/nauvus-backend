import pytest

from nauvus.apps.driver.models import Driver
from nauvus.users.models import User


@pytest.fixture
def driver(faker, user):
    user.user_type = User.DRIVER
    user.save()

    d = Driver.objects.create(user=user)
    return d
