import pytest

from nauvus.services.loadboards.loadboard123.api import Loadboard123


@pytest.mark.django_db
def test_get_load_return_loads():
    result = Loadboard123().get_loads()
    assert result is not None
