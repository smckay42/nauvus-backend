from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DispatcherConfig(AppConfig):
    name = "nauvus.apps.dispatcher"
    verbose_name = _("Dispatcher")
