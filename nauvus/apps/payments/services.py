from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

from nauvus.apps.loads.models import Load
from nauvus.apps.payments.models import Invoice, LoadSettlement, Loan, Payment
from nauvus.services.credit.oatfi.api import Oatfi
from nauvus.services.stripe import StripeClient

stripe_client = StripeClient()
oatfi = Oatfi()


def get_unpaid_invoices_balance_in_cents(carrier_user):
    """Returns the total amount of money from unpaid invoices that is due to the user."""
    unpaid_invoices = Invoice.objects.filter(carrier_user=carrier_user).exclude(status="paid")

    unpaid_invoice_balance = 0
    nauvus_fees = 0
    if unpaid_invoices:
        unpaid_invoice_balance = unpaid_invoices.aggregate(Sum("amount_due_in_cents")).get("amount_due_in_cents__sum")
        nauvus_fees = (
            LoadSettlement.objects.filter(invoice__in=unpaid_invoices)
            .aggregate(Sum("nauvus_fees_in_cents"))
            .get("nauvus_fees_in_cents__sum")
        )

    loans = Loan.objects.filter(invoice__in=unpaid_invoices)

    loan_totals = 0

    # if there are loans, get the balances of the principals and the fees
    if loans:
        loan_subtotals = loans.aggregate(Sum("principal_amount_in_cents"), Sum("fee_amount_in_cents"))
        loan_totals = loan_subtotals.get("principal_amount_in_cents__sum") + loan_subtotals.get(
            "fee_amount_in_cents__sum"
        )

    total_balance = unpaid_invoice_balance - nauvus_fees - loan_totals

    return total_balance


def transfer_nauvus_fees(load_settlement: LoadSettlement) -> Payment:
    """Transfer the fee amount to the Nauvus fees account"""

    transfer_amount = load_settlement.nauvus_fees_in_cents

    if transfer_amount == 0:
        return None
    stripe_transfer = stripe_client.create_transfer(
        transfer_amount, settings.NAUVUS_FEE_ACCOUNT, f"Nauvus fee for load {load_settlement.load.id}"
    )

    transfer_id = stripe_transfer["id"]

    # create the payment and reference the transfer
    payment = Payment.objects.create(
        payment_type=Payment.PaymentType.FEE,
        amount_in_cents=transfer_amount,
        load_settlement=load_settlement,
        stripe_ref_id=transfer_id,
    )

    return payment


def transfer_carrier_balance(invoice: Invoice, amount):
    carrier_account = invoice.carrier_user.user.stripe_customer_id
    stripe_transfer = stripe_client.create_transfer(
        amount, carrier_account, f"Remaining payout for load {invoice.load_settlement.load.id}"
    )
    transfer_id = stripe_transfer["id"]

    # create the payment and reference the transfer
    payment = Payment.objects.create(
        payment_type=Payment.PaymentType.TO_CARRIER,
        amount_in_cents=amount,
        load_settlement=invoice.load_settlement,
        stripe_ref_id=transfer_id,
    )

    return payment


def process_broker_payment(invoice: Invoice, broker_payment: Payment):
    """Distribute the payment from the broker to loan provider and carrier while taking agreed fees"""

    # mark the invoice as paid
    invoice.amount_paid_in_cents = broker_payment.amount_in_cents
    invoice.paid_date = broker_payment.created_at
    invoice.status = "paid"

    invoice.save()

    oatfi.update_invoice(invoice)

    loan_repayment_amount = 0
    try:
        # payback the loan principal and fees
        loan = invoice.loan
        loan_repayment = oatfi.repay_loan(loan)
        loan_repayment_amount = loan_repayment.amount_in_cents

    except ObjectDoesNotExist:
        # if no loan, then no need to process it
        pass

    # transfer nauvus fees to the fees account
    nauvus_fee_payment = transfer_nauvus_fees(invoice.load_settlement)

    # transfer remaining balance to carrier
    balance_due_to_carrier = invoice.amount_due_in_cents - loan_repayment_amount - nauvus_fee_payment.amount_in_cents
    transfer_carrier_balance(invoice, balance_due_to_carrier)

    # as a final step, mark the load as COMPLETED
    invoice.load_settlement.load.current_status = Load.Status.COMPLETED
    invoice.load_settlement.load.save()
