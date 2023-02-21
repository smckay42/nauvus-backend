import pytest
from rest_framework.test import APITestCase

from nauvus.apps.loads.models import Load
from nauvus.apps.payments.models import Loan
from nauvus.apps.payments.services import get_unpaid_invoices_balance_in_cents


@pytest.mark.usefixtures("load_for_testclass", "carrier_user_for_testclass")
class TestInvoice(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.payment_url_base = "/api/v1/payments"
        return super().setUpTestData()

    def setUp(self) -> None:

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

        self.client.force_authenticate(user=self.carrier_user.user)

        return super().setUp()

    @pytest.mark.django_db
    def test_get_unpaid_invoices_balance_no_loan(self):

        balance = get_unpaid_invoices_balance_in_cents(self.carrier_user)

        self.assertGreater(balance, 0)
        expected_total = self.invoice.amount_due_in_cents - self.load_settlement.nauvus_fees_in_cents
        self.assertEqual(balance, expected_total)

    @pytest.mark.django_db
    def test_get_unpaid_invoices_balance_with_loan(self):

        loan_principal_amount = round(self.invoice.amount_due_in_cents * 0.8)
        loan_fee = round(self.invoice.amount_due_in_cents * 0.02)

        Loan.objects.create(
            current_status=Loan.Status.OUTSTANDING,
            terms="terms",
            terms_accepted=True,
            principal_amount_in_cents=loan_principal_amount,
            fee_amount_in_cents=loan_fee,
            invoice=self.invoice,
        )

        balance = get_unpaid_invoices_balance_in_cents(self.carrier_user)

        self.assertGreater(balance, 0)
        expected_total = (
            self.invoice.amount_due_in_cents
            - self.load_settlement.nauvus_fees_in_cents
            - loan_principal_amount
            - loan_fee
        )
        self.assertEqual(balance, expected_total)
