# from django.db import models
from django.db.models import CASCADE, CharField, EmailField, ForeignKey
from django.utils.translation import gettext_lazy as _

# from nauvus.apps.carrier.models import Carrier
# from nauvus.apps.dispatcher.models import Dispatcher
from nauvus.base.models import BaseModel
from nauvus.users.models import User


# Create your models here.
class Invitation(BaseModel):
    class Meta(BaseModel.Meta):
        pass

    DRIVER = "driver"
    DISPATCHER = "dispatcher"
    SECONDARY_USER = "secondary_user"

    INVITATION_TYPES = ((DRIVER, "driver"), (DISPATCHER, "dispatcher"), (SECONDARY_USER, "secondary_user"))

    # status types
    ACCEPT = "accept"
    REJECT = "reject"
    PENDING = "pending"

    STATUS_TYPES = (
        (ACCEPT, "Accept"),
        (REJECT, "Reject"),
        (PENDING, "Pending"),
    )

    # the user sending the invite
    inviter = ForeignKey(User, null=True, blank=True, on_delete=CASCADE, related_name="inviter")

    # the email address of the receipient of the invite
    invitee_email = EmailField(_("Email"), unique=False, null=True, blank=True, default=None)

    invitation_type = CharField(
        _("Invitation Type"),
        null=True,
        blank=True,
        choices=INVITATION_TYPES,
        max_length=200,
    )

    status = CharField(
        _("Status Type"),
        null=True,
        blank=True,
        choices=STATUS_TYPES,
        max_length=200,
    )
