import geopy
from django.db import models
from django_filters import rest_framework as filters

from nauvus.apps.loads.models import Load
from nauvus.utils.location import Location


class LoadFilter(filters.FilterSet):
    def __init__(self, data=None, *args, **kwargs):

        if data is not None:

            # get a mutable copy of the QueryDict
            data = data.copy()

            if "pickup" in data.keys():
                pickup_radius = data.get("pickup_radius", 25)
                pickup = data.get("pickup")
                data["pickup"] = f"{pickup}, {pickup_radius}"

            if "dropoff" in data.keys():
                dropoff_radius = data.get("dropoff_radius", 25)
                dropoff = data.get("dropoff")
                data["dropoff"] = f"{dropoff}, {dropoff_radius}"

        super().__init__(data, *args, **kwargs)

    pickup_date = filters.DateFilter(field_name="pickup_date", method="get_loads_pickup_date")
    dropoff_date = filters.DateFilter(field_name="dropoff_date", method="get_loads_dropoff_date")
    pickup = filters.CharFilter(field_name="origin", method="get_loads_origin")
    dropoff = filters.CharFilter(field_name="destination", method="get_loads_dropoff")
    distance = filters.CharFilter(method="get_loads_distance")

    def get_loads_pickup_date(self, queryset, field_name, value):
        return queryset.filter(pickup_date__date__gte=value).filter(current_status="available")

    def get_loads_dropoff_date(self, queryset, field_name, value):
        return queryset.filter(dropoff_date__date__lte=value).filter(current_status="available")

    def get_loads_origin(self, queryset, field_name, value):
        values_list = value.split(",")
        city = values_list[0]
        state = values_list[1]
        radius = int(values_list[2])

        zipcodes = Location().get_nearby_zipcodes(city=city, state=state, radius=radius)

        return Load.objects.filter(origin__zipcode__in=zipcodes).filter(current_status="available")

    def get_loads_dropoff(self, queryset, field_name, value):
        values_list = value.split(",")
        city = values_list[0]
        state = values_list[1]
        radius = int(values_list[2])

        zipcodes = Location().get_nearby_zipcodes(city=city, state=state, radius=radius)

        return Load.objects.filter(destination__zipcode__in=zipcodes).filter(current_status="available")

    def get_loads_distance(self, queryset, field_name, value):

        loads_to_filter = list()

        for load in queryset:

            origin_coordinates = (load.origin.get("latitude"), load.origin.get("longitude"))
            destination_coordinates = (load.destination.get("latitude"), load.destination.get("longitude"))

            distance = round(geopy.distance.great_circle(origin_coordinates, destination_coordinates).miles)

            if value == "local":
                if distance <= 150:
                    loads_to_filter.append(load.id)
            elif value == "medium":
                if distance >= 150 and distance <= 700:
                    loads_to_filter.append(load.id)
            elif value == "long":
                if distance >= 700:
                    loads_to_filter.append(load.id)

        return Load.objects.filter(id__in=loads_to_filter).filter(current_status="available")

    class Meta:
        model = Load
        fields = ["pickup_date", "dropoff_date", "pickup", "dropoff"]
        filter_overrides = {
            models.ImageField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
            models.JSONField: {
                "filter_class": filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
        }
