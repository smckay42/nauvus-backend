from django.contrib import admin

from nauvus.apps.cities.models import City, Country, State

# Register your models here.


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):

    list_display = ["id", "name", "iso3"]


@admin.register(State)
class StateAdmin(admin.ModelAdmin):

    list_display = ["id", "name", "state_code"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):

    list_display = ["id", "name", "state_id", "country_id"]
