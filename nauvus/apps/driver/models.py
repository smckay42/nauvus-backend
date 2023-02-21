import os

from django.db.models import (
    CASCADE,
    SET_NULL,
    BooleanField,
    CharField,
    DecimalField,
    ForeignKey,
    Index,
    PositiveIntegerField,
    FileField,
)
from django.utils.translation import gettext_lazy as _

from nauvus.apps.carrier.models import Carrier, CarrierUser
from nauvus.apps.vehicle.models import Vehicle
from nauvus.base.models import BaseModel
from nauvus.users.models import User


# Create your models here.
class Driver(BaseModel):

    """Driver model For Carrier Admin Driver"""

    XS = "xs"
    S = "s"
    M = "m"
    L = "l"
    XL = "xl"
    DOUBLE_XL = "2xl"

    T_SHIRT_CHOICE = (
        (XS, "XS"),
        (S, "S"),
        (M, "M"),
        (L, "L"),
        (XL, "XL"),
        (DOUBLE_XL, "2XL"),
    )

    user = ForeignKey(User, on_delete=CASCADE, null=True, blank=True)
    t_shirt_size = CharField(
        _("Driver t-shirt size"),
        null=True,
        blank=True,
        choices=T_SHIRT_CHOICE,
        max_length=20,
    )
    available = BooleanField(default=True)

    class Meta:
        indexes = [
            Index(fields=["id"]),
            Index(fields=["user"]),
        ]


class CarrierDriver(BaseModel):

    carrier = ForeignKey(Carrier, on_delete=CASCADE, null=True, blank=True)
    driver = ForeignKey(Driver, on_delete=CASCADE, null=True, blank=True)
    active = BooleanField(default=True)
    price_visibility = BooleanField(default=True)
    license_number = CharField(
        _("License number"), null=True, blank=True, max_length=100
    )
    commision_percentage = PositiveIntegerField(
        _("Commision percentage of driver"), null=True, blank=True
    )
    vehicle = ForeignKey(
        Vehicle, null=True, blank=True, on_delete=SET_NULL, default=None
    )
    automatic_calculations = BooleanField(
        _("Automatic percentage Calculations"), default=False
    )
    is_owner_operator = BooleanField(
        _("Is Driver Owner Operator"), default=False
    )
    can_manage_load = BooleanField(_("Driver can Manage Load"), default=False)
    can_reject_load = BooleanField(_("Driver can Reject load"), default=False)
    is_current_carrier = BooleanField(_("Is current carrier"), default=True)

    carrier_user = ForeignKey(
        CarrierUser, on_delete=CASCADE, null=True, blank=True, default=None
    )

    def get_latest_by_driver(driver):
        return CarrierDriver.objects.filter()

    class Meta:
        indexes = [
            Index(fields=["id"]),
            Index(fields=["carrier"]),
        ]


class DriverCurrentLocation(BaseModel):

    driver = ForeignKey(Driver, blank=True, null=True, on_delete=CASCADE)
    latitude = DecimalField(
        max_digits=50, decimal_places=10, null=True, blank=True
    )
    longitude = DecimalField(
        max_digits=50, decimal_places=10, null=True, blank=True
    )
    street = CharField(max_length=400, blank=True, null=True)
    city = CharField(max_length=255, blank=True, null=True)
    state = CharField(max_length=255, null=True, blank=True)
    country = CharField(max_length=255, blank=True, null=True)


def wrapper_service_agreement_document(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "{}{}".format(
        "service_agreement" + "-" + str(instance.uid), ext
    )
    return os.path.join(
        "driver/service_agreement/",
        filename,
    )


def path_and_rename_service_agreement_document():
    return wrapper_service_agreement_document

class DriverServiceAgreement(BaseModel):
    """
    Driver service agreement for company service agreement in
    Driver onboarding.
    """

    driver = ForeignKey(Driver, on_delete=CASCADE)
    envelope_id = CharField(_("Driver Envelope ID"), max_length=255)
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
            Index(fields=["driver"]),
        ]

    def __str__(self):
        return self.envelope_id
