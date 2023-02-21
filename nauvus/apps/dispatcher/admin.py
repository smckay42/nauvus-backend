from django.contrib import admin

from nauvus.apps.dispatcher.models import (
    Dispatcher,
    DispatcherInvitation,
    DispatcherReference,
    DispatcherServiceAgreement,
    DispatcherUser,
    DispatcherW9Information,
)

# Register your models here.


@admin.register(Dispatcher)
class DispatcherAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "source",
        "amount_of_experience",
        "organization_name",
    ]


@admin.register(DispatcherUser)
class DispatcherUserAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "user",
        "dispatcher",
        "is_owner",
        "access_type",
        "is_current_organization",
    ]


@admin.register(DispatcherW9Information)
class DispatcherW9InformationAdmin(admin.ModelAdmin):

    list_display = ["id", "dispatcher", "w9_document"]


@admin.register(DispatcherReference)
class DispatcherReference(admin.ModelAdmin):

    list_display = ["id", "company_name"]


@admin.register(DispatcherServiceAgreement)
class DispatcherServiceAgreementReference(admin.ModelAdmin):

    list_display = ["id", "envelope_id", "is_signed"]


@admin.register(DispatcherInvitation)
class DispatcherInvitation(admin.ModelAdmin):

    list_display = ["id", "user", "dispatcher", "active", "commision"]
