import os

from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    EmailField,
    FileField,
    ForeignKey,
    Index,
    PositiveIntegerField,
)
from django.utils.translation import gettext_lazy as _

from nauvus.base.models import BaseModel
from nauvus.users.models import User


# Create your models here.
class Dispatcher(BaseModel):

    """
    Dispatcher model for Nauvus.
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

    CARRIER = "carrier"
    OWNER_OPERATOR = "owner_operator"

    DRIVER_TYPE = ((CARRIER, "Carrier"), (OWNER_OPERATOR, "Owner Operator"))

    source = CharField(
        _("Source"),
        choices=SOURCE_CHOICE,
        max_length=50,
        null=True,
        blank=True,
    )

    amount_of_experience = CharField(
        _("Amount of Experience"), max_length=50, null=True, blank=True
    )
    driver_type = CharField(
        _("Driver Type"),
        choices=DRIVER_TYPE,
        max_length=50,
        null=True,
        blank=True,
    )
    driver_or_carrier_to_onboard = BooleanField(default=True)
    organization_name = CharField(
        _("Name"), max_length=100, null=True, blank=True
    )
    number_of_dispatcher = PositiveIntegerField(
        _("Amount of Dispatcher"), null=True, blank=True
    )
    no_of_drivers = PositiveIntegerField(
        _("No of Drivers"), null=True, blank=True
    )

    class Meta:
        indexes = [
            Index(fields=["id"]),
        ]

    def __str__(self):
        return self.organization_name


def wrapper_w9_info(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "{}.{}".format("w9info" + "-" + str(instance.uid), ext)
    return os.path.join(
        "dispatcher/w9-information/",
        filename,
    )


def path_and_rename_w9_info():
    return wrapper_w9_info


class DispatcherUser(BaseModel):

    """
    Dispatcher User Model
    """

    FULL_ADMIN = "full_admin"
    READ_ONLY_ADMIN = "redy_only_admin"

    ACCESS_TYPE = (
        (FULL_ADMIN, "Full Admin"),
        (READ_ONLY_ADMIN, "Read Only Admin"),
    )

    user = ForeignKey(User, on_delete=CASCADE, null=True, blank=True)
    dispatcher = ForeignKey(
        Dispatcher, on_delete=CASCADE, null=True, blank=True
    )
    is_owner = BooleanField(default=False)
    access_type = CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=ACCESS_TYPE,
        default=READ_ONLY_ADMIN,
    )
    is_current_organization = BooleanField(
        default=False, help_text="To Find the Current Dispatcher Organization"
    )
    permission = CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=ACCESS_TYPE,
        default=READ_ONLY_ADMIN,
    )
    pending_invitation = BooleanField(default=False)

    class Meta:
        indexes = [
            Index(fields=["id"]),
            Index(fields=["user", "access_type"]),
            Index(fields=["user", "is_current_organization"]),
            Index(fields=["dispatcher", "is_owner"]),
            Index(fields=["user", "is_owner"]),
            Index(fields=["user", "dispatcher"]),
        ]

    @staticmethod
    def get_by_user(user):
        try:
            return DispatcherUser.objects.get(user=user)
        except Dispatcher.DoesNotExist():
            return None

    @staticmethod
    def get_current_organization(user):
        dispatcher_user = DispatcherUser.objects.filter(
            user=user, is_current_organization=True
        ).first()
        return dispatcher_user.dispatcher

    @staticmethod
    def get_owner(dispatcher):
        dispatcher_owner = DispatcherUser.objects.filter(
            is_owner=True, dispatcher=dispatcher
        ).first()
        if dispatcher_owner:
            return dispatcher_owner.user
        return None


class DispatcherW9Information(BaseModel):
    """
    DispatcherW9Information for W9 form information
    and taxpayer id number in dispatcher onboarding.
    """

    dispatcher = ForeignKey(
        Dispatcher, null=True, blank=True, on_delete=CASCADE
    )
    w9_document = FileField(
        _("W9 form and and Tax ID Number"),
        null=True,
        blank=True,
        upload_to="dispatcher/dispatcher_w9_information",
    )
    taxpayer_id_number = CharField(_("Tax ID number"), max_length=255)

    class Meta:
        indexes = [
            Index(fields=["id"]),
            Index(fields=["dispatcher"]),
        ]


class DispatcherReference(BaseModel):
    """
    DispatcherReference for company reference in
    Dispatcher onboarding.
    """

    dispatcher = ForeignKey(
        Dispatcher, null=True, blank=True, on_delete=CASCADE
    )
    company_name = CharField(
        _("Company Name"), null=True, blank=True, max_length=255
    )
    driver_name = CharField(
        _("Dirver name"), null=True, blank=True, max_length=255
    )
    email = EmailField(_("Email"), unique=False)
    phone = CharField(_("Phone no"), max_length=20)

    class Meta:
        indexes = [
            Index(fields=["id"]),
            Index(fields=["dispatcher"]),
        ]


def wrapper_service_agreement_document(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "{}{}".format(
        "service_agreement" + "-" + str(instance.uid), ext
    )
    return os.path.join(
        "dispatcher/service_agreement/",
        filename,
    )


def path_and_rename_service_agreement_document():
    return wrapper_service_agreement_document


class DispatcherServiceAgreement(BaseModel):
    """
    Dispatcher service agreement for company serivice agreement in
    Dispatcher onboarding.
    """

    dispatcher = ForeignKey(Dispatcher, on_delete=CASCADE)
    envelope_id = CharField(_("Dispatcher Envelope ID"), max_length=255)
    is_signed = BooleanField(default=False)
    document = FileField(
        _("document"),
        upload_to=path_and_rename_service_agreement_document(),
        blank=True,
        null=True,
    )

    class Meta:
        indexes = [
            Index(fields=["id"]),
            Index(fields=["dispatcher"]),
        ]

    def __str__(self):
        return self.envelope_id


class DispatcherInvitation(BaseModel):

    """Store the information of the Invited Dispatcher."""

    user = ForeignKey(User, on_delete=CASCADE, null=True, blank=True)
    dispatcher = ForeignKey(
        Dispatcher, on_delete=CASCADE, null=True, blank=True
    )
    active = BooleanField(default=True)
    commision = PositiveIntegerField(
        _("Commision of the invited dispatcher"), null=True, blank=True
    )

    class Meta:
        indexes = [
            Index(fields=["id"]),
            Index(fields=["dispatcher"]),
        ]
