from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NauvusAdminConfig(AppConfig):
    name = "nauvus.apps.nauvus_admin"
    verbose_name = _("Nauvus_Admin")
