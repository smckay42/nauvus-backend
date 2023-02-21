import pytest

from nauvus.apps.broker.models import Broker
from nauvus.services.loadboards.loadboard123.api import Loadboard123

@pytest.mark.django_db
def test_create_broker():
    result = Loadboard123().create_broker("371ae47f-115d-44c5-b5bb-2aaf73dd29ca", 698365)
    assert isinstance(result, Broker)
