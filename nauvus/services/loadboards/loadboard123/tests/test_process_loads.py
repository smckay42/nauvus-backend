import pytest

from nauvus.services.loadboards.loadboard123.api import Loadboard123


@pytest.mark.django_db
def test_process_loads():
    result = Loadboard123().process_loads(states=["RI"])
    assert result is not None
