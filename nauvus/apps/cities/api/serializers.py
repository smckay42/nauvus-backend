from django.contrib.auth import get_user_model
from rest_framework import serializers

from nauvus.api.serializers import BaseModelSerializer, BaseSerializer
from nauvus.apps.cities.models import City

User = get_user_model()


class CitySerializer(BaseModelSerializer):

    """Cities Information"""

    state = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ("id", "name", "state", "country")

    def get_state(self, obj):
        return obj.state.state_code

    def get_country(self, obj):
        return obj.country.iso2


class CityDistanceSerializer(BaseModelSerializer):

    """Distance Between two Cities"""

    city = serializers.CharField(max_length=300, required=True)
    state = serializers.CharField(max_length=300, required=True)

    class Meta:
        model = City
        fields = ("city", "state")


class DistanceSerializer(BaseSerializer):

    """Distance Between two Points of city"""

    pickup_location = CityDistanceSerializer()
    dropoff_location = CityDistanceSerializer()
