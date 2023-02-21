from django.contrib import admin

from .models import CarrierDriver, Driver, DriverCurrentLocation

# Register your models here.


@admin.register(Driver)
class DrivermodelAdmin(admin.ModelAdmin):
    list_display = ["id", "user"]


@admin.register(CarrierDriver)
class DriverCarrieModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "carrier",
        "driver",
        "is_current_carrier",
        "carrier_user",
    ]


@admin.register(DriverCurrentLocation)
class DriverCurrentLocationModelAdmin(admin.ModelAdmin):
    list_display = ["id", "driver", "city"]
