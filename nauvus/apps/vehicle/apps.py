from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VehicleConfig(AppConfig):
    name = "nauvus.apps.vehicle"
    verbose_name = _("Vehicle")
