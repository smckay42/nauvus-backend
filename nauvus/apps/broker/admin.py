from django.contrib import admin

from nauvus.apps.broker.models import Broker, BrokerPlatForm

# Register your models here.


@admin.register(BrokerPlatForm)
class BrokerPlatFormAdmin(admin.ModelAdmin):

    list_display = ["id", "name"]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):

    list_display = ["id", "name", "phone"]
