import pytest

from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.users.models import User
from nauvus.utils.helpers import create_user


@pytest.fixture
def dispatcher_user(faker, dispatcher):
    user = create_user(faker)
    user.user_type = User.DISPATCHER
    user.save()

    du = DispatcherUser.objects.create(user=user, dispatcher=dispatcher)
    return du


@pytest.fixture
def dispatcher(faker):
    d = Dispatcher.objects.create(
        organization_name=f"{faker.company()} Dispatchers",
    )

    return d
