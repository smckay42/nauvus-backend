import mimetypes
import os
import uuid

from django.db import models
from django.forms import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nauvus.apps.broker.models import Broker
from nauvus.apps.carrier.models import Carrier
from nauvus.apps.dispatcher.models import DispatcherUser
from nauvus.apps.driver.models import Driver
from nauvus.users.models import User


def upload_to(instance, filename):
    now = timezone.now()
    base, extension = os.path.splitext(filename.lower())
    milliseconds = now.microsecond
    return f"rc_documents/{now:%Y%m%d%H%M%S}{milliseconds}{extension}"


def upload_complete_delivery_documents_to(instance, filename):
    now = timezone.now()
    base, extension = os.path.splitext(filename.lower())
    milliseconds = now.microsecond
    return f"complete_delivery_documents/{now:%Y%m%d%H%M%S}{milliseconds}{extension}"


def validate_document_file(document):
    # 5 MB
    limit_file_size = 5000000
    valid_content_types = ["image/jpeg", "image/png", "application/pdf"]

    file_mime_type = mimetypes.guess_type(document.name)[0]

    if file_mime_type not in valid_content_types:
        raise forms.ValidationError("Invalid file format!", code="invalid")

    if document.size > limit_file_size:
        raise forms.ValidationError(f"Please keep filesize under 5MB. Current filesize {document.size}")
    return document


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    class Meta:
        abstract = True


class AccessToken(BaseModel):
    loadboard_name = models.CharField(max_length=300, null=True, blank=True)
    access_token = models.CharField(max_length=2000, null=True, blank=True)
    refresh_token = models.CharField(max_length=2000, null=True, blank=True)
    expires = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = "access_tokens"


class LoadSource(BaseModel):
    source = models.CharField(max_length=300, null=True, blank=True)
    load_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "load_source"


class Load(BaseModel):
    """

    Please, consult Postman to check the content of dictionaries for fields origin, destination, details, and contact.

    """

    class Status(models.TextChoices):
        AVAILABLE = "available", _("AVAILABLE")
        BOOKED = "booked", _("BOOKED")
        PENDING = "pending", _("PENDING")
        UPCOMING = "upcoming", _("UPCOMING")
        UNDERWAY = "underway", _("UNDERWAY")
        DELIVERED = "delivered", _("DELIVERED")
        PARTIAL_SETTLED = "partial_settled", _("PARTIAL_SETTLED")
        COMPLETED = "completed", _("COMPLETED")
        DRAFT = "draft", _("DRAFT")

    source = models.ForeignKey(LoadSource, null=True, blank=True, on_delete=models.PROTECT)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    origin = models.JSONField(default=dict, blank=True)
    destination = models.JSONField(default=dict, blank=True)
    pickup_date = models.DateTimeField(null=True, blank=True)
    dropoff_date = models.DateTimeField(null=True, blank=True)
    current_status = models.CharField(max_length=50, default="", choices=Status.choices, blank=True)
    broker = models.ForeignKey(Broker, null=True, blank=True, on_delete=models.PROTECT)
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.PROTECT)
    dispatcher = models.ForeignKey(DispatcherUser, null=True, blank=True, on_delete=models.PROTECT)
    carrier = models.ForeignKey(Carrier, null=True, blank=True, on_delete=models.PROTECT)
    details = models.JSONField(default=dict, blank=True)
    contact = models.JSONField(default=dict, blank=True)
    posted_rate = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    rc_document = models.FileField(
        _("Rate Confirmation Document"),
        upload_to=upload_to,
        blank=True,
        null=True,
        validators=[validate_document_file],
    )
    final_rate = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    reference_title = models.CharField(max_length=100, null=False, blank=False, default="Load without Ref")
    estimated_mileage = models.IntegerField(null=True, blank=True)
    invoice_email = models.EmailField(null=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "loads"

    def get_carrier(self):
        return self.carrier


class LoadStatusHistory(BaseModel):
    load_id = models.ForeignKey(Load, null=True, blank=True, on_delete=models.PROTECT)
    status = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "load_status_history"


class DeliveryDocument(BaseModel):
    load_id = models.ForeignKey(Load, null=True, blank=True, on_delete=models.PROTECT)
    document = models.FileField(
        upload_to=upload_complete_delivery_documents_to,
        blank=False,
        null=True,
        validators=[validate_document_file],
    )

    class DocumentType(models.TextChoices):
        BILL_OF_LADING = "bill_of_lading", _("BILL_OF_LADING")
        LUMPER_RECEIPT = "lumper_receipt", _("LUMPER_RECEIPT")
        OTHER = "other", _("OTHER")

    document_type = models.CharField(
        max_length=50, default=DocumentType.OTHER, choices=DocumentType.choices, blank=False
    )
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "delivery_documents"
