from django.db import models
from django.db.models import CASCADE, CharField, ForeignKey, PositiveIntegerField
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Country(models.Model):

    id = PositiveIntegerField(_("id"), primary_key=True)
    name = CharField(_("name"), max_length=255, null=True, blank=True)
    iso3 = CharField(_("iso3"), max_length=255, null=True, blank=True)
    iso2 = CharField(_("iso2"), max_length=255, null=True, blank=True)
    numeric_code = CharField(
        _("numeric_code"), max_length=255, null=True, blank=True
    )
    phone_code = CharField(
        _("phone_code"), max_length=255, null=True, blank=True
    )
    capital = CharField(_("capital"), max_length=255, null=True, blank=True)
    currency = CharField(_("currency"), max_length=255, null=True, blank=True)
    region = CharField(_("region"), max_length=255, null=True, blank=True)
    subregion = CharField(
        _("subregion"), max_length=255, null=True, blank=True
    )
    latitude = CharField(_("latitude"), max_length=255, null=True, blank=True)
    longitude = CharField(
        _("longitude"), max_length=255, null=True, blank=True
    )

    class Meta:
        indexes = [models.Index(fields=["name"])]


class State(models.Model):

    id = PositiveIntegerField(_("id"), primary_key=True)
    name = CharField(_("id"), max_length=255, null=True, blank=True)
    country = ForeignKey(Country, on_delete=CASCADE)
    state_code = CharField(
        _("state_code"), max_length=255, null=True, blank=True
    )
    state_type = CharField(
        _("city_type"), max_length=255, null=True, blank=True
    )
    latitude = CharField(_("latitude"), max_length=255, null=True, blank=True)
    longitude = CharField(
        _("longitude"), max_length=255, null=True, blank=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["state_code"]),
            models.Index(fields=["name", "country"]),
        ]


class City(models.Model):

    id = PositiveIntegerField(_("id"), primary_key=True)
    name = CharField(_("name"), max_length=255, null=True, blank=True)
    state = ForeignKey(State, on_delete=CASCADE)
    country = ForeignKey(Country, on_delete=CASCADE)
    latitude = CharField(_("latitude"), max_length=255, null=True, blank=True)
    longitude = CharField(
        _("longitude"), max_length=255, null=True, blank=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["state"]),
            models.Index(fields=["country"]),
            models.Index(fields=["name", "state"]),
        ]
