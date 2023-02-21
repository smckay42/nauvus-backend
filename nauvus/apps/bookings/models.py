import os
from datetime import date

from django.db.models import (
    CASCADE,
    DO_NOTHING,
    BooleanField,
    CharField,
    DateTimeField,
    FileField,
    FloatField,
    ForeignKey,
    IntegerField,
    JSONField,
    TextField,
)
from django.utils.translation import gettext_lazy as _

from nauvus.apps.broker.models import Broker, BrokerPlatForm
from nauvus.apps.carrier.models import Carrier, CarrierBroker
from nauvus.apps.dispatcher.models import Dispatcher
from nauvus.apps.driver.models import Driver
from nauvus.base.models import BaseModel
from nauvus.users.models import User

# Create your models here.


class LoadItem(BaseModel):
    source = ForeignKey(
        BrokerPlatForm, on_delete=DO_NOTHING, null=True, blank=True
    )
    commodity = CharField(max_length=300, null=True, blank=True)
    external_load_id = CharField(max_length=300, null=True, blank=True)
    age = CharField(max_length=300, null=True, blank=True)
    posted_date = CharField(max_length=300, null=True, blank=True)
    received_at = CharField(max_length=300, null=True, blank=True)
    computed_miledge = CharField(max_length=300, null=True, blank=True)
    miledge = CharField(max_length=300, null=True, blank=True)
    origin_city = CharField(max_length=300, null=True, blank=True)
    origin_state = CharField(max_length=300, null=True, blank=True)
    origin_country = CharField(max_length=300, null=True, blank=True)
    origin_geolocation_latitude = CharField(
        max_length=300, null=True, blank=True
    )
    origin_geolocation_longitude = CharField(
        max_length=300, null=True, blank=True
    )
    origin_deadhead = CharField(max_length=300, null=True, blank=True)
    destination_city = CharField(max_length=300, null=True, blank=True)
    destination_state = CharField(max_length=300, null=True, blank=True)
    destination_country = CharField(max_length=300, null=True, blank=True)
    destination_geolocation_latitude = CharField(
        max_length=300, null=True, blank=True
    )
    destination_geolocation_longitude = CharField(
        max_length=300, null=True, blank=True
    )
    equipment_type = CharField(max_length=300, null=True, blank=True)
    pickup_date = CharField(max_length=300, null=True, blank=True)
    # pickup_date_time = CharField(max_length=300, null=True, blank=True)
    pickup_date_time = DateTimeField(null=True, blank=True, default=None)
    # pickup_date_time_utc = CharField(max_length=300, null=True, blank=True)
    pickup_date_time_utc = DateTimeField(null=True, blank=True, default=None)
    amount = CharField(max_length=300, null=True, blank=True)
    amount_type = CharField(max_length=100, null=True, blank=True)
    load_size = CharField(max_length=300, null=True, blank=True)
    load_length = CharField(max_length=300, null=True, blank=True)
    load_weight = CharField(max_length=300, null=True, blank=True)
    number_of_stops = IntegerField(null=True, blank=True)
    team_driving = BooleanField(default=False, null=True, blank=True)
    load_status = CharField(max_length=100, null=True, blank=True)
    is_ocfp = BooleanField(null=True, blank=True)
    metadata = JSONField(null=True, blank=True)
    broker = ForeignKey(Broker, on_delete=CASCADE)
    price = FloatField(null=True, blank=True)


def wrapper_rate_confirmation_document(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "{}{}".format(
        "rate-confirmation" + "-" + str(instance.uid), ext
    )
    return os.path.join(
        "bookings/rate-confirmation/",
        filename,
    )


def path_and_rename_rate_confirmation_document():
    return wrapper_rate_confirmation_document


class BookLoad(BaseModel):

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    UPCOMING = "upcoming"

    STATUS_CHOICE = (
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
        (UPCOMING, "Upcoming"),
    )

    DISPATCHER = "dispatcher"
    CARRIER = "carrier"
    DRIVER = "driver"

    BOOKING_CHOICE = (
        (DISPATCHER, "Dispatcher"),
        (CARRIER, "Carrier"),
        (DRIVER, "Driver"),
    )

    load = ForeignKey(LoadItem, on_delete=CASCADE)
    carrier = ForeignKey(Carrier, on_delete=DO_NOTHING)
    driver = ForeignKey(Driver, on_delete=DO_NOTHING)
    status = CharField(
        _("Status"), max_length=100, choices=STATUS_CHOICE, default=UPCOMING
    )
    user = ForeignKey(User, on_delete=DO_NOTHING)
    dispatcher = ForeignKey(
        Dispatcher, on_delete=DO_NOTHING, null=True, blank=True
    )
    book_by = CharField(
        _("Booking Choice"),
        max_length=100,
        choices=BOOKING_CHOICE,
        null=True,
        blank=True,
    )
    rate_confirmation_document = FileField(
        _("Rate Confirmation"),
        upload_to=path_and_rename_rate_confirmation_document(),
        blank=True,
        null=True,
    )
    final_price = FloatField(null=True, blank=True)


def wrapper_proof(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "{}{}".format("proof" + "-" + str(instance.uid), ext)
    return os.path.join(
        "bookings/delivery/proof/",
        filename,
    )


def wrapper_signature(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "{}{}".format("signature" + "-" + str(instance.uid), ext)
    return os.path.join(
        "bookings/delivery/driver-signature/",
        filename,
    )


def path_and_rename_proof():
    return wrapper_proof


def path_and_rename_signature():
    return wrapper_signature


class BookLoadDeliveryProof(BaseModel):

    book_load = ForeignKey(BookLoad, on_delete=CASCADE)
    proof = FileField(
        _("Proof"),
        upload_to=path_and_rename_proof(),
        blank=True,
        null=True,
    )
    signature = FileField(
        _("Signature"),
        upload_to=path_and_rename_signature(),
        blank=True,
        null=True,
    )
    # def __str__(self):
    #     return self.id


class FavouriteLoad(BaseModel):

    commodity = CharField(max_length=300, null=True, blank=True)
    external_load_id = CharField(max_length=300, null=True, blank=True)
    age = CharField(max_length=300, null=True, blank=True)
    posted_date = CharField(max_length=300, null=True, blank=True)
    received_at = CharField(max_length=300, null=True, blank=True)
    computed_miledge = CharField(max_length=300, null=True, blank=True)
    miledge = CharField(max_length=300, null=True, blank=True)
    origin_city = CharField(max_length=300, null=True, blank=True)
    origin_state = CharField(max_length=300, null=True, blank=True)
    origin_country = CharField(max_length=300, null=True, blank=True)
    origin_geolocation_latitude = CharField(
        max_length=300, null=True, blank=True
    )
    origin_geolocation_longitude = CharField(
        max_length=300, null=True, blank=True
    )
    origin_deadhead = CharField(max_length=300, null=True, blank=True)
    destination_city = CharField(max_length=300, null=True, blank=True)
    destination_state = CharField(max_length=300, null=True, blank=True)
    destination_country = CharField(max_length=300, null=True, blank=True)
    destination_geolocation_latitude = CharField(
        max_length=300, null=True, blank=True
    )
    destination_geolocation_longitude = CharField(
        max_length=300, null=True, blank=True
    )
    equipment_type = CharField(max_length=300, null=True, blank=True)
    pickup_date = CharField(max_length=300, null=True, blank=True)
    pickup_date_time = CharField(max_length=300, null=True, blank=True)
    pickup_date_time_utc = CharField(max_length=300, null=True, blank=True)
    amount = CharField(max_length=300, null=True, blank=True)
    amount_type = CharField(max_length=100, null=True, blank=True)
    load_size = CharField(max_length=300, null=True, blank=True)
    load_length = CharField(max_length=300, null=True, blank=True)
    load_weight = CharField(max_length=300, null=True, blank=True)
    number_of_stops = IntegerField(null=True, blank=True)
    team_driving = BooleanField(default=False, null=True, blank=True)
    load_status = CharField(max_length=100, null=True, blank=True)
    is_ocfp = BooleanField(null=True, blank=True)
    metadata = JSONField(null=True, blank=True)
    is_favourite = BooleanField(default=True)
    user = ForeignKey(User, on_delete=DO_NOTHING)


class ExternalLoad(BaseModel):

    """EXternal Load Booking Model"""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    UPCOMING = "upcoming"

    STATUS_CHOICE = (
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
        (UPCOMING, "Upcoming"),
    )

    carrier = ForeignKey(Carrier, null=True, blank=True, on_delete=DO_NOTHING)
    dispatcher = ForeignKey(
        Dispatcher, null=True, blank=True, on_delete=DO_NOTHING
    )
    rc_document = FileField(
        _("Rc Document of the Load"),
        upload_to="booking/rc_document",
        blank=True,
        null=True,
    )
    customer_reference_number = CharField(
        null=True, blank=True, max_length=200
    )
    pickup_address_city = CharField(
        _("Name of the Pickup Point City"),
        null=True,
        blank=True,
        max_length=200,
    )
    pickup_address_state = CharField(
        _("Name of the Pickup Point state"),
        null=True,
        blank=True,
        max_length=200,
    )
    pickup_address_zipcode = CharField(
        _("Pickup Point zipcode"),
        null=True,
        blank=True,
        max_length=200,
    )
    dropoff_address_city = CharField(
        _("Name of the Dropoff Point City"),
        null=True,
        blank=True,
        max_length=200,
    )
    dropoff_address_state = CharField(
        _("Name of the Dropoff Point state"),
        null=True,
        blank=True,
        max_length=200,
    )
    dropoff_address_zipcode = CharField(
        _("Name of the Dropoff Point zipcode"),
        null=True,
        blank=True,
        max_length=200,
    )
    pickup_contact_name = CharField(
        _("pickup point contact name"),
        null=True,
        blank=True,
        max_length=200,
    )
    pickup_phone_number = CharField(
        _("phone number of the pickup point"),
        null=True,
        blank=True,
        max_length=200,
    )
    pickup_email = CharField(
        _("email of the of the pickup point"),
        null=True,
        blank=True,
        max_length=200,
    )
    pickup_number = CharField(
        _("pickup number of the of the pickup point"),
        null=True,
        blank=True,
        max_length=200,
    )
    pickup_additional_notes = CharField(
        _("additional notes of the pickup point"),
        null=True,
        blank=True,
        max_length=200,
    )
    dropoff_contact_name = CharField(
        _("contact name of dropoff point"),
        null=True,
        blank=True,
        max_length=200,
    )
    dropoff_phone_number = CharField(
        _("phone number  of dropoff point"),
        null=True,
        blank=True,
        max_length=200,
    )
    dropoff_email = CharField(
        _("email of the dropoff point"),
        null=True,
        blank=True,
        max_length=200,
    )
    dropoff_number = CharField(
        _("dropoff number of the of the dropoff point"),
        null=True,
        blank=True,
        max_length=200,
    )
    dropoff_additional_notes = CharField(
        _("additional notes of the dropoff point"),
        null=True,
        blank=True,
        max_length=200,
    )
    pickup_date = CharField(
        _("Load pickup date"), null=True, blank=True, max_length=200
    )
    dropoff_date = CharField(
        _("Load Dropoff date"), null=True, blank=True, max_length=200
    )
    weight = CharField(
        _("weight of the load"), null=True, blank=True, max_length=200
    )
    load_price = CharField(
        _("Price of the Load"), null=True, blank=True, max_length=200
    )
    broker = ForeignKey(
        CarrierBroker, null=True, blank=True, on_delete=DO_NOTHING
    )
    driver = ForeignKey(Driver, null=True, blank=True, on_delete=DO_NOTHING)
    packging_type = CharField(
        _("packging Type of the load"), null=True, blank=True, max_length=200
    )
    equipment_type = CharField(
        _("equipment_type"), null=True, blank=True, max_length=200
    )
    is_book_by_dispatcher = BooleanField(
        _("Dispatcher add external load"), default=False
    )
    status = CharField(
        _("Status"), max_length=100, choices=STATUS_CHOICE, default=UPCOMING
    )


class BookLoadLiveShare(BaseModel):

    book_load = ForeignKey(
        BookLoad, null=True, blank=True, on_delete=DO_NOTHING
    )
    expiration_date = DateTimeField(null=True, blank=True)


class BookLoadNotes(BaseModel):

    book_load = ForeignKey(
        BookLoad, null=True, blank=True, on_delete=DO_NOTHING
    )
    description = TextField()
