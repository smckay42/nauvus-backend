from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InvitationsConfig(AppConfig):
    name = "nauvus.apps.invitations"
    verbose_name = _("Invitations")
