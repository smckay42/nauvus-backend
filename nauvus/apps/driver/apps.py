from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DriverConfig(AppConfig):
    name = "nauvus.apps.driver"
    verbose_name = _("Driver")
