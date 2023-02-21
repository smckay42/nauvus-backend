from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from nauvus.api.permissions import IsCarrier, IsCarrierOrDispatcher
from nauvus.api.viewsets import BaseModelViewSet
from nauvus.apps.carrier.models import CarrierDispatcher, CarrierUser
from nauvus.apps.dispatcher.models import DispatcherUser
from nauvus.apps.driver.api.serializer import (
    DriverGeolocationUpdateSerializer,
    DriverSerializer,
    DriverUpdateSerializer,
    DriverUserCreateSerializer,
)
from nauvus.apps.driver.models import CarrierDriver, Driver, DriverCurrentLocation
from nauvus.apps.driver.utils import get_bool

User = get_user_model()


class DriverViewSet(BaseModelViewSet):

    """
    create:
        Add Driver

    retrieve:
        Get Driver

    update:
        Update Driver

    destroy:
        Delete Driver

    """

    serializer_class = DriverUserCreateSerializer
    ordering_fields = (
        "   ",
        "user__first_name",
        "user__username",
        "user__phone",
        "available",
    )
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        actions = {
            "create": [
                IsCarrier,
            ],
            "retrieve": [
                IsCarrierOrDispatcher,
            ],
            "list": [
                IsCarrierOrDispatcher,
            ],
            "update": [
                IsCarrier,
            ],
            "delete": [
                IsCarrier,
            ],
        }

        if self.action in actions:
            self.permission_classes += actions.get(self.action)

        return super().get_permissions()

    def get_queryset(self):
        is_active = get_bool(self.request.query_params.get("active"))
        price_visibility = get_bool(self.request.query_params.get("price_visibility"))
        if (
            self.request.user.user_type == User.CARRIER_OWNER
            or self.request.user.user_type == User.CARRIER_OWNER_OPERATOR
        ):
            try:
                carrier_user = CarrierUser.objects.get(user=self.request.user, is_current_organization=True)
            except CarrierUser.DoesNotExist:
                raise NotFound("Carrier User Not Found.")

            carrier_drivers = CarrierDriver.objects.filter(carrier=carrier_user.carrier)

        elif self.request.user.user_type == User.DISPATCHER:

            try:
                dispatcher_user = DispatcherUser.objects.get(
                    user=self.request.user,
                )

                # carrier_dispatcher = CarrierDispatcher.objects.filter(
                #     dispatcher=dispatcher_user.dispatcher,
                # ).in_bulk(['CarrierDispatcher'], field_name="carrier_id")

                carrier_dispatcher = CarrierDispatcher.objects.filter(
                    dispatcher=dispatcher_user.dispatcher,
                ).values_list("carrier")

            except DispatcherUser.DoesNotExist:
                raise NotFound("Dispatcher User Not Found.")

            carrier_drivers = CarrierDriver.objects.filter(carrier__in=list(carrier_dispatcher))

        elif self.request.user.user_type == User.DRIVER:
            raise NotFound("Permission Denied..")

        if is_active is not None:
            carrier_drivers = carrier_drivers.filter(active=is_active)

        if price_visibility is not None:
            carrier_drivers = carrier_drivers.filter(price_visibility=price_visibility)

        carrier_drivers = carrier_drivers.values_list("driver__id", flat=True)

        drivers = Driver.objects.filter(id__in=carrier_drivers)

        return drivers

    def get_serializer_class(self):
        actions = {
            "create": DriverUserCreateSerializer,
            "update": DriverUpdateSerializer,
            "retrive": DriverSerializer,
            "list": DriverSerializer,
            "update_geolocation": DriverGeolocationUpdateSerializer,
        }

        if self.action in actions:
            self.serializer_class = actions.get(self.action)

        return super().get_serializer_class()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(DriverSerializer(user).data)

    def retrieve(self, request, pk=None):
        try:
            driver = Driver.objects.get(id=pk)
        except Exception:
            raise NotFound("Driver not found")

        return Response(DriverSerializer(driver).data)

    def update(self, request, pk=None):
        try:
            driver = Driver.objects.get(id=pk)
        except Exception:
            raise NotFound("Driver Not Found")
        serializer = self.get_serializer(driver, data=request.data)
        serializer.is_valid(raise_exception=True)
        driver = serializer.save()

        return Response(data=DriverSerializer(driver).data)

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=permission_classes,
        url_path="update-location",
    )
    def update_geolocation(self, request, pk):
        drivers = self.get_queryset()
        try:
            driver = drivers.get(pk=pk)
        except Exception:
            raise NotFound("Driver Not Found")
        serializer = self.get_serializer(driver, data=request.data)
        serializer.is_valid(raise_exception=True)
        driver = serializer.save()
        driver_current_location = DriverCurrentLocation.objects.filter(driver=driver).first()
        if driver_current_location:
            driver_current_location.latitude = serializer.validated_data.get("latitude")
            driver_current_location.longitude = serializer.validated_data.get("longitude")
            driver_current_location.street = serializer.validated_data.get("street")
            driver_current_location.city = serializer.validated_data.get("city")
            driver_current_location.state = serializer.validated_data.get("state")
            driver_current_location.country = serializer.validated_data.get("country")
            driver_current_location.save()
        else:
            driver_current_location = DriverCurrentLocation.objects.create(
                driver=driver,
                latitude=serializer.validated_data.get("latitude"),
                longitude=serializer.validated_data.get("longitude"),
                street=serializer.validated_data.get("street"),
                city=serializer.validated_data.get("city"),
                state=serializer.validated_data.get("state"),
                country=serializer.validated_data.get("country"),
            )
        return Response(data=DriverSerializer(driver).data)
