from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BookingsConfig(AppConfig):
    name = "nauvus.apps.bookings"
    verbose_name = _("Bookings")
