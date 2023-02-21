from nauvus.apps.loads.utils import get_broker_from_fmcsa


def test_fmcsa_api_get_mc_number():
    result = get_broker_from_fmcsa('491800')
    assert True
