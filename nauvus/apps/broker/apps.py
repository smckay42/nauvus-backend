from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BrokerConfig(AppConfig):
    name = "nauvus.apps.broker"
    verbose_name = _("Broker")
