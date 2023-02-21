import os

from django.db import models
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    EmailField,
    FileField,
    ForeignKey,
    PositiveIntegerField,
    SlugField,
)

# from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from nauvus.apps.broker.models import BrokerPlatForm
from nauvus.apps.dispatcher.models import Dispatcher
from nauvus.base.models import BaseModel
from nauvus.users.models import User


# Create your models here.
class Carrier(BaseModel):
    """
    Carrier model for Nauvus.
    """

    SOCIAL_MEDIA = "social_media"
    EMAIl = "email"
    BLOG = "blog"
    OTHER = "other"

    SOURCE_CHOICE = (
        (SOCIAL_MEDIA, "Social Media"),
        (EMAIl, "Email"),
        (BLOG, "Blog"),
        (OTHER, "Other"),
    )

    organization_name = CharField(_("Name"), max_length=100, null=True, blank=True)
    source = CharField(
        _("Source"),
        choices=SOURCE_CHOICE,
        max_length=50,
        null=True,
        blank=True,
    )
    no_of_trucks = PositiveIntegerField(help_text="How many vehicles do you have", default=0, null=True, blank=True)
    no_of_trailers = PositiveIntegerField(help_text="How many trailers do you have?", default=0, null=True, blank=True)
    factoring_company_name = CharField(_("Factoring Company"), max_length=100, null=True, blank=True)
    gross_weekly_revenue = CharField(_("Gross Weekly Revenue"), max_length=100, null=True, blank=True)
    mc_number = CharField(_("MC Number"), max_length=100, null=True, blank=True)
    dot_number = CharField(_("DOT Number"), max_length=100, null=True, blank=True)
    fleet_id = SlugField(unique=True, blank=True, null=True, max_length=200)
    street1 = CharField(_("Street1 Address"), null=True, blank=True, max_length=100)
    street2 = CharField(_("Street2 Address"), null=True, blank=True, max_length=100)
    city = CharField(_("City"), null=True, blank=True, max_length=50)
    state = CharField(_("State"), null=True, blank=True, max_length=50)
    zip_code = CharField(_("Zip"), null=True, blank=True, max_length=10)
    invoice_email = EmailField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["id"]),
        ]

    def __str__(self):
        return self.organization_name

    # def save(self, *args, **kwargs):
    #     print("➡ organization_name :", self.organization_name)
    #     print("➡ created_at :", self.created_at)
    #     self.fleet_id = (
    #         slugify(self.organization_name)
    #         + slugify(self.created_at.time())
    #         + slugify(self.created_at.date().day)
    #         + slugify(self.created_at.date().month)
    #         + slugify(self.id)
    #         + slugify(self.created_at.date().year)
    #     )
    #     return super().save(*args, **kwargs)


class CarrierUser(BaseModel):

    """Carrier User Model"""

    FULL_ADMIN = "full_admin"
    READ_ONLY_ADMIN = "redy_only_admin"

    ACCESS_TYPE = (
        (FULL_ADMIN, "Full Admin"),
        (READ_ONLY_ADMIN, "Read Only Admin"),
    )

    user = ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=CASCADE,
    )
    carrier = ForeignKey(Carrier, null=True, blank=True, on_delete=CASCADE)
    is_owner = BooleanField(default=False)
    access_type = CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=ACCESS_TYPE,
        default=READ_ONLY_ADMIN,
    )
    is_current_organization = BooleanField(default=False, help_text="To find Current Carrier Organization")
    # permission = CharField(
    #     max_length=20,
    #     null=True,
    #     blank=True,
    #     choices=ACCESS_TYPE,
    #     default=READ_ONLY_ADMIN,
    # )
    pending_invitation = BooleanField(default=False)

    @staticmethod
    def get_by_user(user):
        try:
            return CarrierUser.objects.get(user=user)
        except CarrierUser.DoesNotExist():
            return None

    @staticmethod
    def get_current_organization(user):
        carrier_user = CarrierUser.objects.filter(user=user).filter(is_current_organization=True).first()
        if carrier_user:
            return carrier_user.carrier
        return None

    @staticmethod
    def get_owner(carrier):
        carrier_owner = CarrierUser.objects.filter(is_owner=True, carrier=carrier).first()
        if carrier_owner:
            return carrier_owner.user
        return None

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["carrier"]),
            models.Index(fields=["user", "is_current_organization"]),
            models.Index(fields=["carrier", "is_owner"]),
            models.Index(fields=["user", "access_type"]),
            models.Index(fields=["user", "is_owner"]),
            models.Index(fields=["user", "carrier"]),
        ]


class CarrierTrailerType(BaseModel):

    DRY_VAN = "dry_van"
    REEFER = "reefer"
    FLATBED = "flatbed"
    STEP_DECK = "step_deck"
    BOX_TRUCK = "box_truck"
    HOTSHOT = "hotshot"
    POWER_ONLY = "power_only"
    OTHER = "other"

    TRAILER_TYPE = (
        (DRY_VAN, "Dry Van"),
        (REEFER, "Reefer"),
        (FLATBED, "Flatbed"),
        (STEP_DECK, "Step Deck"),
        (BOX_TRUCK, "Box Truck"),
        (HOTSHOT, "Hotshot"),
        (POWER_ONLY, "Power Only"),
        (OTHER, "Other"),
    )

    trailer_type = CharField(
        _("Trailer Type"),
        choices=TRAILER_TYPE,
        max_length=50,
        null=True,
        blank=True,
    )
    carrier = ForeignKey(Carrier, null=True, blank=True, on_delete=CASCADE)


class CarrierTrailerSize(BaseModel):

    FEET_48 = "48_eet"
    FEET_40 = "40_feet"
    FEET_45 = "45_feet"
    FEET_53 = "53_feet"
    OTHER = "other"

    TRAILER_SIZE = (
        (FEET_48, "Feet 48"),
        (FEET_40, "Feet 40"),
        (FEET_45, "Feet 45"),
        (FEET_53, "Feet 53"),
        (OTHER, "Other"),
    )
    trailer_size = CharField(
        _("Trailer Size"),
        choices=TRAILER_SIZE,
        max_length=50,
        null=True,
        blank=True,
    )
    carrier = ForeignKey(Carrier, null=True, blank=True, on_delete=CASCADE)


# Wrapper for operating authority letter
def wrapper_operating_authority_letter(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "{}{}".format("operating-authority-letter" + "-" + str(instance.uid), ext)
    return os.path.join(
        "carrier/fleet-application/operating-authority-letter/",
        filename,
    )


def path_and_rename_operating_authority_letter():
    return wrapper_operating_authority_letter


# Wrapper for insurance certificate
def wrapper_insurance_certificate(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "{}{}".format("insurance-certificate" + "-" + str(instance.uid), ext)
    return os.path.join(
        "carrier/fleet-application/insurance-certificate/",
        filename,
    )


def path_and_rename_insurance_certificate():
    return wrapper_insurance_certificate


# Wrapper for business documentation
def wrapper_business_documentation(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "{}{}".format("business-documentation" + "-" + str(instance.uid), ext)
    return os.path.join(
        "carrier/fleet-application/business-documentation/",
        filename,
    )


def path_and_rename_business_documentation():
    return wrapper_business_documentation


class CarrierFleetApplication(BaseModel):

    carrier = ForeignKey(Carrier, null=True, blank=True, on_delete=CASCADE)
    operating_authority_letter = FileField(
        _("Authority Letter"),
        upload_to=path_and_rename_operating_authority_letter(),
    )
    insurance_certificate = FileField(
        _("Insurance Certificate"),
        upload_to=path_and_rename_insurance_certificate(),
    )
    business_documentation = FileField(
        _("Business Documentation"),
        upload_to=path_and_rename_business_documentation(),
    )

    class Meta:
        indexes = [
            models.Index(fields=["carrier"]),
        ]

    def __str__(self):
        return self.carrier.organization_name


class CarrierBroker(BaseModel):

    carrier = ForeignKey(Carrier, null=True, blank=True, on_delete=CASCADE)
    broker = ForeignKey(BrokerPlatForm, on_delete=models.CASCADE)
    username = CharField(_("Username"), max_length=50)
    password = CharField(_("password"), max_length=20)

    class Meta:
        indexes = [
            models.Index(fields=["id"]),
            models.Index(fields=["carrier"]),
        ]


def wrapper_w9_info(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "{}{}".format("w9info" + "-" + str(instance.uid), ext)
    return os.path.join(
        "carrier/w9-information/",
        filename,
    )


def path_and_rename_w9_info():
    return wrapper_w9_info


class CarrierW9Information(BaseModel):

    carrier = ForeignKey(Carrier, null=True, blank=True, on_delete=CASCADE)
    w9_document = FileField(
        _("W-9 Document"),
        upload_to=path_and_rename_w9_info(),
    )
    taxpayer_ID_number = CharField(_("Taxpayer ID"), blank=True, null=True, max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=["id"]),
            models.Index(fields=["carrier"]),
        ]


def wrapper_service_agreement_document(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "{}{}".format("service_agreement" + "-" + str(instance.uid), ext)
    return os.path.join(
        "carrier/service_agreement/",
        filename,
    )


def path_and_rename_service_agreement_document():
    return wrapper_service_agreement_document


class CarrierServiceAgreement(BaseModel):

    carrier = ForeignKey(
        Carrier,
        null=True,
        blank=True,
        on_delete=CASCADE,
    )
    envelope_id = CharField(_("Carrier Envelope ID"), max_length=255)
    is_signed = BooleanField(default=False)
    document = FileField(
        _("document"),
        upload_to=path_and_rename_service_agreement_document(),
        blank=True,
        null=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["id"]),
            models.Index(fields=["carrier"]),
        ]

    def __str__(self):
        return self.envelope_id


class CarrierDispatcher(BaseModel):

    """Carrier Dispatcher model"""

    user = ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=CASCADE,
    )
    carrier = ForeignKey(
        Carrier,
        null=True,
        blank=True,
        on_delete=CASCADE,
    )
    dispatcher = ForeignKey(
        Dispatcher,
        null=True,
        blank=True,
        on_delete=CASCADE,
    )
    active = BooleanField(_("Status of the Carrier dispatcher"), default=True)

    class Meta:
        indexes = [
            models.Index(fields=["id"]),
            models.Index(fields=["carrier"]),
            models.Index(fields=["carrier", "active"]),
            models.Index(fields=["dispatcher", "active"]),
            models.Index(fields=["dispatcher"]),
        ]
