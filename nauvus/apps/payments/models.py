from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _

from nauvus.apps.broker.models import Broker
from nauvus.apps.carrier.models import CarrierUser
from nauvus.apps.loads.models import Load
from nauvus.base.models import BaseModel
from nauvus.services.email_client import EmailClient
from nauvus.utils.conversion import convert_date_to_ms_since_epoch


class LoadSettlement(BaseModel):
    load = models.OneToOneField(Load, null=False, blank=False, on_delete=models.PROTECT)

    nauvus_fee_percent = models.DecimalField(null=False, default=0.0, max_digits=4, decimal_places=2)
    nauvus_fees_in_cents = models.IntegerField(null=False, blank=False, default=0)
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_timestamp = models.DateTimeField(null=True, blank=True)

    def accept_terms(self, terms_accepted_time):
        """User accepts the terms; if there is a loan accept those terms too"""
        self.terms_accepted = True
        self.terms_accepted_timestamp = terms_accepted_time

        # if there is a loan present, then we should accept the loan terms too
        try:
            loan = self.invoice.loan
            loan.terms_accepted = True
            loan.terms_accepted_timestamp = terms_accepted_time

        except ObjectDoesNotExist:
            pass


class LoadSettlementStatusHistory(BaseModel):
    load_settlement_id = models.ForeignKey(LoadSettlement, null=True, blank=True, on_delete=models.PROTECT)
    status = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "load_settlement_status_history"


class Invoice(BaseModel):
    """An invoice to the broker to pay the agreed rate for the completion of delivery."""

    broker = models.ForeignKey(Broker, null=True, blank=True, on_delete=models.PROTECT)
    carrier_user = models.ForeignKey(CarrierUser, null=True, blank=True, on_delete=models.PROTECT)

    due_date = models.DateField(null=True, blank=True)

    amount_due_in_cents = models.PositiveIntegerField(null=False, blank=False)
    amount_paid_in_cents = models.PositiveIntegerField(null=False, default=0, blank=False)

    # the date the invoice is fully paid
    paid_date = models.DateField(null=True, blank=True)

    description = models.TextField(null=False, blank=False)

    load_settlement = models.OneToOneField(LoadSettlement, null=False, blank=False, on_delete=models.PROTECT)

    stripe_payment_link = models.CharField(max_length=255, null=True, blank=True)
    stripe_payment_id = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(max_length=255, null=True, blank=True, default="unpaid")

    def due_date_in_milliseconds(self):
        return convert_date_to_ms_since_epoch(self.due_date)

    def paid_date_in_milliseconds(self):
        return convert_date_to_ms_since_epoch(self.paid_date)

    def send(self):
        """Sends the invoice to the broker"""
        load = self.load_settlement.load
        link = self.stripe_payment_link
        delivery_docs = load.deliverydocument_set.all()
        rc_document = load.rc_document.path

        context = {
            "invoice": self,
            "load_id": load.id,
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "rate": float(self.amount_due_in_cents) / 100,
            "stripe_payment_link": link,
        }

        # Send the Invoice
        subject = "Nauvus Invoice"
        receiver = self.load_settlement.load.invoice_email
        template_name = "payments/invoice.html"

        attachments = [document_file.document.path for document_file in delivery_docs]
        attachments.append(rc_document)

        EmailClient().send_html_email(subject, receiver, template_name, context, attachments)


class InvoiceStatusHistory(BaseModel):
    invoice_id = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.PROTECT)
    status = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "invoice_status_history"


class Loan(BaseModel):
    """A loan for part of the balance of a load payment."""

    class Status(models.TextChoices):
        OFFERED = "offered", _("OFFERED")
        OUTSTANDING = "outstanding", _("OUTSTANDING")
        CLOSED = "closed", _("CLOSED")
        LATE = "late", _("LATE")
        DEFAULT = "default", _("DEFAULT")

    # in the future, we may have multiple loan providers, let's use this to track it
    class Source(models.TextChoices):
        OATFI = "oatfi", _("OATFI")

    principal_amount_in_cents = models.PositiveIntegerField(null=False, blank=False)
    fee_amount_in_cents = models.PositiveIntegerField(null=False, blank=False)

    lender = models.CharField(max_length=50, default="", choices=Source.choices, blank=True)
    lender_loan_id = models.CharField(max_length=50, blank=True, null=True)

    current_status = models.CharField(max_length=50, default="", choices=Status.choices, blank=True)

    invoice = models.OneToOneField(Invoice, null=False, blank=False, on_delete=models.PROTECT)

    terms = models.TextField(null=False, blank=False)
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_timestamp = models.DateTimeField(null=True, blank=True)


class LoanStatusHistory(BaseModel):
    loan_id = models.ForeignKey(Loan, null=True, blank=True, on_delete=models.PROTECT)
    status = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "loan_status_history"


class Payment(BaseModel):
    class PaymentType(models.TextChoices):
        TO_CARRIER = "to_carrier", _("TO_CARRIER")
        FROM_BROKER = "from_broker", _("FROM_BROKER")
        FEE = "fee", _("FEE")
        LOAN_REPAYMENT = "loan_repayment", _("LOAN_REPAYMENT")
        LOAN_PAYOUT = "loan_payout", _("LOAN_PAYOUT")

    amount_in_cents = models.PositiveIntegerField(null=False, blank=False)
    load_settlement = models.ForeignKey(LoadSettlement, null=False, blank=False, on_delete=models.PROTECT)
    stripe_ref_id = models.CharField(max_length=300, null=False, blank=False)
    payment_type = models.CharField(max_length=30, null=False, blank=False, choices=PaymentType.choices)
