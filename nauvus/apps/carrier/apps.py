from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class CarrierConfig(AppConfig):
    name = "nauvus.apps.carrier"
    verbose_name = _("Carrier")

    def ready(self):
        import nauvus.apps.carrier.signals