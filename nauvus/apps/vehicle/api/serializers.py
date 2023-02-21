from rest_framework import serializers

from nauvus.api.serializers import BaseModelSerializer
from nauvus.apps.carrier.models import CarrierUser
from nauvus.apps.vehicle.models import Vehicle
from rest_framework.exceptions import NotFound


class VehicleCreateSerializer(BaseModelSerializer):

    """Add Vehicle For the Carrier Organization"""

    vehicle_type = serializers.DictField(child=serializers.CharField())
    licence_plate = serializers.DictField(child=serializers.CharField())

    class Meta:
        model = Vehicle
        fields = (
            # "carrier",
            "vehicle_ID",
            "VIN",
            "vehicle_type",
            "fuel_type",
            "licence_plate",
            "odometer",
        )

    # def validate(self, data):

    def validate_vehicle_ID(self, value):
        request = self.context.get("request")
        user = CarrierUser.objects.filter(user=request.user).first()
        vehicles = Vehicle.objects.filter(
            carrier=user.carrier, vehicle_ID=value
        )
        if vehicles:
            raise serializers.ValidationError(
                "Vehicle is already exist with the given vehicle_ID number."
            )

        return value

    def create(self, validated_data):
        request = self.context.get("request")

        try:
            carrier_user = CarrierUser.objects.get(
                user=request.user,
                is_current_organization=True,
                access_type=CarrierUser.FULL_ADMIN,
            )
            carrier = carrier_user.carrier
        except Exception:
            raise NotFound("Carrier User Not Found.")

        vehicle_data = validated_data.get("vehicle_type")
        licence_plate = validated_data.get("licence_plate")

        vehicle = Vehicle(
            carrier=carrier,
            vehicle_ID=validated_data.get("vehicle_ID"),
            VIN=validated_data.get("VIN"),
            vehicle_year=vehicle_data.get("vehicle_year"),
            vehicle_make=vehicle_data.get("vehicle_make"),
            vehicle_model=vehicle_data.get("vehicle_model"),
            fuel_type=validated_data.get("fuel_type"),
            state=licence_plate.get("state"),
            number=licence_plate.get("number"),
            odometer=validated_data.get("odometer"),
            # active=False,
        )
        vehicle.save()

        return vehicle


class VehicleTypeSerializer(BaseModelSerializer):

    """Vehicle type"""

    class Meta:
        model = Vehicle
        fields = ("vehicle_year", "vehicle_make", "vehicle_model")


class VehicleLicencePlateSeriaizer(BaseModelSerializer):

    """Information about vehicle license plate number"""

    class Meta:
        model = Vehicle
        fields = ("state", "number")


class VehicleUpdateSerializer(BaseModelSerializer):

    """Update the information about vehicle"""

    vehicle_type = VehicleTypeSerializer()
    licence_plate = VehicleLicencePlateSeriaizer()

    class Meta:
        model = Vehicle
        fields = (
            "carrier",
            "vehicle_ID",
            "VIN",
            "vehicle_type",
            "fuel_type",
            "licence_plate",
            "odometer",
        )

    def validate_vehicle_ID(self, value):
        request = self.context.get("request")

        carrier = CarrierUser.objects.filter(user=request.user).first()
        vehicles = Vehicle.objects.filter(
            carrier=carrier.carrier, vehicle_ID=value
        )

        if self.instance:
            vehicles = vehicles.exclude(pk=self.instance.pk)
        if vehicles:
            raise serializers.ValidationError(
                "Vehicle is already exist with the given vehicle_ID number."
            )

        return value

    def update(self, instance, validated_data):

        vehicle_data = validated_data.get("vehicle_type")
        licence_plate = validated_data.get("licence_plate")

        instance.carrier = validated_data.get("carrier")
        instance.vehicle_ID = validated_data.get("vehicle_ID")
        instance.VIN = validated_data.get("VIN")
        instance.vehicle_year = vehicle_data.get("vehicle_year")
        instance.vehicle_make = vehicle_data.get("vehicle_make")
        instance.vehicle_model = vehicle_data.get("vehicle_model")
        instance.fuel_type = validated_data.get("fuel_type")
        instance.state = licence_plate.get("state")
        instance.number = licence_plate.get("number")
        instance.odometer = validated_data.get("odometer")
        instance.save()

        return instance


class VehicleSerializer(BaseModelSerializer):

    """Response Serializer for vehicle Information."""

    licence_plate = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = (
            "id",
            "vehicle_ID",
            "VIN",
            "fuel_type",
            "licence_plate",
            "active",
            "vehicle_year",
            "vehicle_make",
            "vehicle_model",
        )

    def get_licence_plate(self, obj):

        return VehicleLicencePlateSeriaizer(obj).data


class VehiclesByCarrierSerializer(BaseModelSerializer):

    """List of vehicle for individual carrier organization"""

    licence_plate = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = (
            "id",
            "vehicle_ID",
            "vehicle_make",
            "vehicle_model",
            "licence_plate",
            "active",
        )

    def get_licence_plate(self, obj):

        return VehicleLicencePlateSeriaizer(obj).data


class VehicleStatusSerializer(BaseModelSerializer):

    """Current Status of the vehicle"""

    class Meta:
        model = Vehicle
        fields = ("active",)


class VehicleInformationSerializer(BaseModelSerializer):

    """Vehicle Information Serializer"""

    class Meta:
        model = Vehicle
        exclude = ("carrier", "uid", "created_at", "updated_at")
