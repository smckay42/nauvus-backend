from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    ForeignKey,
    Index,
    PositiveIntegerField,
)
from django.utils.translation import gettext_lazy as _

from nauvus.apps.carrier.models import Carrier
from nauvus.base.models import BaseModel


# Create your models here.
class Vehicle(BaseModel):

    """
    Vehicle model for Carrier Admin
    """

    DIESEL = "diesel"
    PETROL = "petrol"
    GAS = "gas"

    FUEL_CHOICE = (
        (DIESEL, "Diesel"),
        (PETROL, "Petrol"),
        (GAS, "Gas"),
    )

    MILES = "miles"
    KILOMETERS = "kilometers"

    ODOMETER_CHOICE = (
        (MILES, "Miles"),
        (KILOMETERS, "Kilometers"),
    )

    carrier = ForeignKey(Carrier, on_delete=CASCADE)
    vehicle_ID = PositiveIntegerField(_("Vehicle ID"))
    VIN = CharField(_("Vehicle VIN"), max_length=100)
    vehicle_year = CharField(_("Vehicle Year"), max_length=10)
    vehicle_make = CharField(_("Vehicle Make"), max_length=100)
    vehicle_model = CharField(_("Vehicle Model"), max_length=100)
    fuel_type = CharField(_("Fuel Type"), choices=FUEL_CHOICE, max_length=20)
    state = CharField(_("Vehicle State"), max_length=50)
    number = CharField(_("Vehicle Number"), max_length=20)
    odometer = CharField(_("Odometer"), choices=ODOMETER_CHOICE, max_length=20)
    active = BooleanField(_("Is Active"), default=True)

    class Meta:
        indexes = [
            Index(fields=["id"]),
            Index(fields=["carrier"]),
            Index(fields=["active"]),
        ]

    def __str__(self):
        return f"{self.vehicle_ID} - {self.vehicle_model}"

    @staticmethod
    def get_vehicle_id(id):
        try:
            return Vehicle.objects.get(id=id)
        except Vehicle.DoesNotExist:
            return None
