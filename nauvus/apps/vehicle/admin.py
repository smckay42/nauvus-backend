from django.contrib import admin

from nauvus.apps.vehicle.models import Vehicle


# Register your models here.
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):

    list_display = ["id", "carrier", "vehicle_ID", "VIN"]
