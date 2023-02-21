from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from nauvus.api.permissions import IsCarrier
from nauvus.api.viewsets import BaseModelViewSet
from nauvus.apps.carrier.models import CarrierUser
from nauvus.apps.vehicle.models import Vehicle

from .serializers import (
    VehicleCreateSerializer,
    VehicleSerializer,
    VehicleStatusSerializer,
    VehicleUpdateSerializer,
)


class VehicleViewset(BaseModelViewSet):

    """
    create:
        Add Vehicle

    retrieve:
        Get Vehicle

    update:
        Update Vehicle

    destroy:
        Delete Vehicle

    manage_vehicle_status:
        Manage Vehicle Status
    """

    serializer_class = VehicleCreateSerializer

    ordering_fields = ("id", "vehicle_ID", "state", "number", "active")

    permission_classes = [IsAuthenticated, IsCarrier]

    def get_queryset(self):
        # carrier = self.request.query_params.get("carrier", None)

        vehicle_status = self.request.query_params.get("status", "")

        # if carrier:
        #     carrier = CarrierUser.objects.filter(
        #         user=self.request.user
        #     ).first()
        #     vehicles = Vehicle.objects.filter(carrier=carrier.carrier)
        # else:
        try:
            carrier = CarrierUser.objects.get(
                user=self.request.user, is_current_organization=True
            )
        except Exception:
            raise NotFound("Carrier User Not Found.")
        vehicles = Vehicle.objects.filter(carrier=carrier.carrier)

        if vehicle_status == "active":
            vehicles = vehicles.filter(active=True)
        elif vehicle_status == "inactive":
            vehicles = vehicles.filter(active=False)
        return vehicles

    def get_serializer_class(self):
        actions = {
            "create": VehicleCreateSerializer,
            "update": VehicleUpdateSerializer,
            "retrieve": VehicleSerializer,
            "list": VehicleSerializer,
            "manage_vehicle_status": VehicleStatusSerializer,
        }

        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vehicle = serializer.save()
        return Response(
            data=VehicleSerializer(vehicle, context={"request": request}).data
        )

    def update(self, request, pk=None):

        try:
            vehicle = Vehicle.objects.get(id=pk)
        except Vehicle.DoesNotExist:
            raise NotFound("Vehicle not found")

        serializer = self.get_serializer(vehicle, data=request.data)
        serializer.is_valid(raise_exception=True)
        vehicle = serializer.save()

        return Response(
            data=VehicleSerializer(vehicle, context={"request": request}).data
        )

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAuthenticated, IsCarrier],
        url_path="manage-vehicle-status",
    )
    def manage_vehicle_status(self, request, pk):

        try:
            vehicles = self.get_queryset()
            vehicle = vehicles.get(id=pk)
        except Vehicle.DoesNotExist:
            raise NotFound("Vehicle not found")

        serializer = self.get_serializer(vehicle, data=request.data)
        serializer.is_valid(raise_exception=True)
        vehicle = serializer.save()
        return Response(data=VehicleSerializer(vehicle).data)
