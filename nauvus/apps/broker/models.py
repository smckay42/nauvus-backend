import os

from django.db.models import CharField, ImageField, Index, JSONField
from django.utils.translation import gettext_lazy as _

from nauvus.base.models import BaseModel

# from nauvus.services.credit.oatfi.api import Oatfi


def wrapper_source_image(instance, filename):
    name, ext = os.path.splitext(filename)
    filename = "{}{}".format("source-image" + "-" + str(instance.uid), ext)
    return os.path.join(
        "broker-platform/source-image/",
        filename,
    )


def path_and_rename_source_iamge():
    return wrapper_source_image


# TODO: clean this up.  no longer needed
class BrokerPlatForm(BaseModel):

    name = CharField(_("name"), max_length=50, blank=True, null=True)
    image = ImageField(_("Source Image"), upload_to=path_and_rename_source_iamge(), default="")

    class Meta:
        indexes = [
            Index(fields=["id"]),
            Index(fields=["name"]),
        ]

    @staticmethod
    def get_object_dict_by_name(name):
        try:
            broker_platform = BrokerPlatForm.objects.get(name=name)
            data = {
                "name": broker_platform.name if broker_platform.name else None,
                "image": broker_platform.image.url if broker_platform.image else None,
            }
            return data
        except BrokerPlatForm.DoesNotExist:
            return {}


class Broker(BaseModel):

    external_broker_id = CharField(_("Load Broker ID"), max_length=300, null=True, blank=True)
    name = CharField(_("Name"), max_length=300, null=True, blank=True)
    phone = CharField(_("phone"), max_length=300, null=True, blank=True)
    email = CharField(_("email"), max_length=300, null=True, blank=True)
    mc_number = CharField(_("MC Number"), max_length=300, null=True, blank=True)
    dot_number = CharField(_("DOT Number"), max_length=300, null=True, blank=True)
    metadata = JSONField(_("Metadata"), null=True, blank=True)
    contact_first_name = CharField(_("contact first name"), max_length=300, null=True, blank=True)
    contact_last_name = CharField(_("contact last name"), max_length=300, null=True, blank=True)
    street1 = CharField(_("Street1 Address"), null=True, blank=True, max_length=100)
    street2 = CharField(_("Street2 Address"), null=True, blank=True, max_length=100)
    city = CharField(_("City"), null=True, blank=True, max_length=50)
    state = CharField(_("State"), null=True, blank=True, max_length=50)
    zip_code = CharField(_("Zip"), null=True, blank=True, max_length=10)
