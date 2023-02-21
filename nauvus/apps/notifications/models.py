from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    ForeignKey,
    TextField,
)
from django.utils.translation import gettext_lazy as _

from nauvus.apps.bookings.models import BookLoad, BookLoadDeliveryProof
from nauvus.apps.carrier.models import Carrier, CarrierUser
from nauvus.apps.dispatcher.models import Dispatcher
from nauvus.apps.driver.models import Driver
from nauvus.base.models import BaseModel
from nauvus.users.models import User


# Create your models here.
class Notification(BaseModel):

    RATE_CONFIRMATION = "rate_confirmation"
    DELIVERY_PROOF = "delivery_proof"
    DRIVER_RESPONSE = "driver_response"
    BOOK_LOAD = "book_load"
    ASSIGN_DRIVER_TO_LOAD = "assign_driver_to_load"

    NOTIFICATION_TYPES = (
        (RATE_CONFIRMATION, "Rate Confirmation"),
        (DELIVERY_PROOF, "Delivery Proof"),
        (DRIVER_RESPONSE, "Driver Response"),
        (BOOK_LOAD, "Book Load"),
        (ASSIGN_DRIVER_TO_LOAD, "Assign Driver To Load"),
    )

    notification_type = CharField(
        _("Notification Type"),
        null=True,
        blank=True,
        choices=NOTIFICATION_TYPES,
        max_length=100,
    )

    user = ForeignKey(
        User, null=True, blank=True, on_delete=CASCADE, default=None
    )

    carrier = ForeignKey(
        Carrier, null=True, blank=True, on_delete=CASCADE, default=None
    )

    dispatcher = ForeignKey(
        Dispatcher, on_delete=CASCADE, null=True, blank=True, default=None
    )

    driver = ForeignKey(
        Driver, on_delete=CASCADE, null=True, blank=True, default=None
    )
    external_load_id = CharField(max_length=300, null=True, blank=True)

    delivery_proof = ForeignKey(
        BookLoadDeliveryProof,
        on_delete=CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    driver_response_for_load = BooleanField(default=False)
    reason = TextField(max_length=1000)
    carrier_user = ForeignKey(
        CarrierUser, on_delete=CASCADE, null=True, blank=True, default=None
    )

    book_load = ForeignKey(
        BookLoad, on_delete=CASCADE, null=True, blank=True, default=None
    )

    is_seen = BooleanField(default=False)

    @staticmethod
    def create_delivery_proof_notification(
        book_load_obj=None,
        delivery_proof_obj=None,
        driver_obj=None,
        carrier_obj=None,
        dispatcher_obj=None,
    ):

        notification = Notification.objects.create(
            book_load=book_load_obj,
            delivery_proof=delivery_proof_obj,
            driver=driver_obj,
            carrier=carrier_obj,
            dispatcher=dispatcher_obj,
            notification_type=Notification.DELIVERY_PROOF,
        )

        return notification

    @staticmethod
    def create_driver_response_for_load_notification(
        response,
        mongo_load_id=None,
        reason=None,
        driver_obj=None,
        carrier_obj=None,
        dispatcher_obj=None,
    ):

        notification = Notification.objects.create(
            external_load_id=mongo_load_id,
            driver_response_for_load=response,
            reason=reason,
            driver=driver_obj,
            carrier=carrier_obj,
            dispatcher=dispatcher_obj,
            notification_type=Notification.DRIVER_RESPONSE,
        )

        return notification

    @staticmethod
    def create_assign_driver_to_load_notification(
        book_load_obj=None,
        # mongo_load_id=None,
        carrier_obj=None,
        dispatcher_obj=None,
        driver_obj=None,
        user_obj=None,
    ):

        notification = Notification.objects.create(
            book_load=book_load_obj,
            user=user_obj,
            # external_load_id=mongo_load_id,
            carrier=carrier_obj,
            dispatcher=dispatcher_obj,
            driver=driver_obj,
            notification_type=Notification.ASSIGN_DRIVER_TO_LOAD,
        )

        return notification

    @staticmethod
    def create_booked_load_notification(
        book_load_obj=None,
        carrier_obj=None,
        dispatcher_obj=None,
        driver_obj=None,
    ):

        notification = Notification.objects.create(
            book_load=book_load_obj,
            carrier=carrier_obj,
            dispatcher=dispatcher_obj,
            driver=driver_obj,
            notification_type=Notification.BOOK_LOAD,
        )

        return notification

    @staticmethod
    def create_rate_confirmation_notification(
        book_load_obj=None,
        user_obj=None,
        carrier_obj=None,
        dispatcher_obj=None,
    ):

        notification = Notification.objects.create(
            book_load=book_load_obj,
            user=user_obj,
            carrier=carrier_obj,
            dispatcher=dispatcher_obj,
            notification_type=Notification.RATE_CONFIRMATION,
        )

        return notification
