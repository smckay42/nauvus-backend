import time

import pytest

from nauvus.apps.loads.models import AccessToken
from nauvus.services.loadboards.loadboard123.api import Loadboard123


@pytest.mark.django_db
@pytest.fixture
def access_token(db):
    return AccessToken.objects.create(loadboard_name="123LOADBOARD", access_token='1234567890',
                                      refresh_token='987654321',
                                      expires=round(time.time()) + 2000)


@pytest.mark.django_db
def test_get_access_token_token_does_not_exist():
    result = Loadboard123().get_access_token()
    assert result is True


def test_get_access_token_already_created(access_token):
    result = Loadboard123().get_access_token()
    assert result is True
