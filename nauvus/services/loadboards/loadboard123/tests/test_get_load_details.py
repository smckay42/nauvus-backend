import pytest

from nauvus.services.loadboards.loadboard123.api import Loadboard123

@pytest.mark.django_db
def test_get_load_details():
    result = Loadboard123().get_load_details("2b1ba6e3-f8c9-4f04-97ea-0e7352082cec")
    assert result is not None
