import pytest
from rest_framework.test import APITestCase

from nauvus.services.credit.oatfi.api import Oatfi

oatfi = Oatfi()


@pytest.mark.usefixtures("carrier_user_for_testclass")
class TestCarrier(APITestCase):
    def setUp(self) -> None:
        return super().setUp()

    @pytest.mark.django_db
    def test_create_carrier_user(self):
        carrier_user = self.carrier_user
        carrier_user.user.save()
        carrier_user.carrier.save()
        carrier_user.save()

        # check to ensure that the business got created
        info = oatfi.get_business_information(carrier_user)

        assert info["externalId"] == str(carrier_user.carrier.uid)
