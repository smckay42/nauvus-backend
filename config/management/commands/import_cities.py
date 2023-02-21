import environ
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command

from nauvus.apps.cities.data.city2 import cities
from nauvus.apps.cities.data.country import countries
from nauvus.apps.cities.data.state import states
from nauvus.apps.cities.models import City, Country, State


class Command(BaseCommand):
    help = "Seeds initial data for the application."
    ENV = environ.Env()

    def __init__(self):
        self.user_class = get_user_model()
        super().__init__()

    def handle(self, *args, **options):
        # self.create_country()
        # self.create_state()
        self.create_city()

    def create_country(self):

        for country in countries:
            try:
                Country.objects.update_or_create(
                    id=country["id"],
                    name=country["name"],
                    iso3=country["iso3"],
                    iso2=country["iso2"],
                    numeric_code=country["numeric_code"],
                    phone_code=country["phone_code"],
                    capital=country["capital"],
                    currency=country["currency"],
                    region=country["region"],
                    subregion=country["subregion"],
                    latitude=country["latitude"],
                    longitude=country["longitude"],
                )
            except Exception as e:
                print(
                    "::::: Country :: {}, {} :: {}".format(
                        country["id"], country["name"], str(e)
                    )
                )

    def create_state(self):

        for state in states:
            try:
                country = Country.objects.get(id=state["country_id"])
                State.objects.update_or_create(
                    id=state["id"],
                    name=state["name"],
                    country=country,
                    state_code=state["state_code"],
                    state_type=state["type"],
                    latitude=state["latitude"],
                    longitude=state["longitude"],
                )
            except Exception as e:
                print(
                    "::::: State :: {}, {} :: {}".format(
                        state["id"], state["name"], str(e)
                    )
                )

    def create_city(self):

        for city in cities:
            print(city["name"])
            try:
                state = State.objects.get(id=city["state_id"])
                City.objects.update_or_create(
                    id=city["id"],
                    name=city["name"],
                    state=state,
                    country=state.country,
                    latitude=city["latitude"],
                    longitude=city["longitude"],
                )
            except Exception as e:
                print(
                    "::::: City :: {}, {} :: {}".format(
                        city["id"], city["name"], str(e)
                    )
                )
