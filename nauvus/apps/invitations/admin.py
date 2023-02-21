from django.contrib import admin

from nauvus.apps.invitations.models import Invitation

# Register your models here.


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "inviter",
        "invitee_email",
        "invitation_type",
        "status",
    ]
