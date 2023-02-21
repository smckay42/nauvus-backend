from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CitiesAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nauvus.apps.cities"
    verbose_name = _("Cities")
