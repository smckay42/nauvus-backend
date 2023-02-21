import pytest
from rest_framework.test import APITestCase

from nauvus.apps.loads.models import Load
from nauvus.apps.payments.models import Payment
from nauvus.services.credit.oatfi.api import Oatfi


@pytest.mark.usefixtures("load_for_testclass", "carrier_user_for_testclass")
class TestOatfi(APITestCase):
    oatfi = Oatfi()

    def setUp(self) -> None:
        # saving the broker and the carrier will ensure they are already in Oatfi
        self.carrier_user.user.save()
        self.carrier_user.carrier.save()
        self.carrier_user.save()
        self.carrier_driver.driver.user.save()
        self.carrier_driver.driver.save()
        self.carrier_driver.save()
        self.load.broker.save()
        self.load.current_status = Load.Status.DELIVERED
        self.load.driver = self.carrier_driver.driver
        self.load.save()
        self.load_settlement.save()
        self.invoice.carrier_user = self.carrier_user
        self.invoice.save()

    def test_repay_loan(self):
        self.oatfi.save_carrier(self.carrier_user)

        self.oatfi.send_invoice_history([self.invoice])

        loan = self.oatfi.get_loan_offer(self.invoice)

        self.assertIsNotNone(loan)
        self.oatfi.accept_loan(loan)

        # TODO: transfer the money in from the stripe test bank to ensure there is always $
        # in the account

        response = self.oatfi.repay_loan(loan)

        self.assertIs(type(response), Payment)

        self.assertEqual(
            Payment.objects.filter(
                load_settlement=self.load_settlement, payment_type=Payment.PaymentType.LOAN_REPAYMENT
            ).count(),
            1,
        )
