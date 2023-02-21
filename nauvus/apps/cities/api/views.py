import geopy.distance
from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from nauvus.api.viewsets import BaseListRetrieveViewSet, BaseModelViewSet
from nauvus.apps.cities.api.serializers import (
    CitySerializer,
    DistanceSerializer,
)
from nauvus.apps.cities.models import City


class CityViewset(BaseListRetrieveViewSet):

    """
    create:
        Add Cities

    update:
        Update Cities

    retrieve:
        Get Cities

    destroy:
        Delete Cities

    list:
        List Cities
    """

    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        country_ids = [39, 233]
        qs = City.objects.filter(country__id__in=country_ids)
        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(state__name__icontains=search)
                | Q(country__name__icontains=search)
            )
        # else:
        #     qs = City.objects.filter()
        return qs

    def get_serializer_class(self):
        actions = {
            "list": CitySerializer,
        }

        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()


class DistanceView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = DistanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            pickup_location = City.objects.get(
                name=serializer.data.get("pickup_location").get("city"),
                state__state_code=serializer.data.get("pickup_location").get(
                    "state"
                ),
            )
        except City.DoesNotExist:
            raise NotFound("pickup_location City Not Found.")

        try:
            dropoff_location = City.objects.get(
                name=serializer.data.get("dropoff_location").get("city"),
                state__state_code=serializer.data.get("dropoff_location").get(
                    "state"
                ),
            )
        except City.DoesNotExist:
            raise NotFound("dropoff_location City Not Found.")

        origin = (pickup_location.latitude, pickup_location.longitude)
        destination = (
            dropoff_location.latitude,
            dropoff_location.longitude,
        )

        distance = geopy.distance.geodesic(origin, destination).km

        response = {}
        response["distance"] = distance
        return Response(response)
