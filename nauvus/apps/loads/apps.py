from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LoadsConfig(AppConfig):
    name = "nauvus.apps.loads"
    verbose_name = _("Loads")
