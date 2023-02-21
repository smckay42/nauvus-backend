from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from nauvus.api.serializers import BaseModelSerializer
from nauvus.apps.carrier.models import CarrierUser
from nauvus.apps.driver.models import CarrierDriver, Driver, DriverCurrentLocation
from nauvus.apps.vehicle.models import Vehicle

User = get_user_model()


class DriverUserCreateSerializer(BaseModelSerializer):

    """Add Driver for the Carrier Organization"""

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    phone = serializers.CharField()
    password = serializers.CharField()
    available = serializers.BooleanField(required=True)
    vehicle = serializers.IntegerField()
    t_shirt_size = serializers.CharField()
    license_number = serializers.CharField()
    active = serializers.BooleanField(required=True)
    price_visibility = serializers.BooleanField(required=True)
    commision_percentage = serializers.CharField()
    automatic_calculations = serializers.BooleanField(required=True)
    is_owner_operator = serializers.BooleanField(required=True)
    can_manage_load = serializers.BooleanField(required=True)
    can_reject_load = serializers.BooleanField(required=True)
    add_yourself_as_a_driver = serializers.BooleanField(required=True)

    class Meta:
        model = Driver
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "phone",
            "password",
            "available",
            "vehicle",
            "t_shirt_size",
            "license_number",
            "active",
            "price_visibility",
            "commision_percentage",
            "automatic_calculations",
            "is_owner_operator",
            "can_manage_load",
            "can_reject_load",
            "add_yourself_as_a_driver",
        ]
        read_only_fields = ["id"]

    def validate_username(self, value):
        users = User.objects.filter(username=value)

        if self.instance:
            users = users.exclude(pk=self.instance.user.pk)

        if users:
            raise serializers.ValidationError("User is alreday exist with this username.")
        return value

    def validate_phone(self, value):
        users = User.objects.filter(phone=value)

        if self.instance:
            users = users.exclude(pk=self.instance.user.pk)

        if users:
            raise serializers.ValidationError("User is alreday exist with this phone.")
        return value

    def validate_vehicle(self, value):
        try:
            Vehicle.objects.get(id=value)
        except Exception:
            raise serializers.ValidationError("Provided vehicle is invalid.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        # Crate User
        user = User(
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            username=request.data.get("username"),
            phone=validated_data.get("phone"),
            user_type=User.DRIVER,
        )
        user.set_password(validated_data["password"])
        user.save()

        # Crate Driver
        driver = Driver(
            user=user,
            available=validated_data.get("available", True),
            t_shirt_size=validated_data.get("t_shirt_size"),
        )
        driver.save()
        # carrier = CarrierUser.objects.filter(user=request.user).first()
        vehicle = Vehicle.objects.get(id=validated_data.get("vehicle"))
        carrier = CarrierUser.objects.filter(user=request.user).first()

        try:
            vehicle = Vehicle.objects.get(id=validated_data.get("vehicle"), carrier=carrier.carrier)
        except Exception:
            raise NotFound("Vehicle is Not Associate With the Carrier")

        # if validated_data.get("add_yourself_as_a_driver") == True:
        try:
            carrier_user = CarrierUser.objects.get(
                user=request.user,
                access_type=CarrierUser.FULL_ADMIN,
                is_current_organization=True,
            )
        except CarrierUser.DoesNotExist:
            raise NotFound("Carrier User Not Found.")

        if validated_data.get("add_yourself_as_a_driver") is True:
            try:
                CarrierDriver.objects.get(carrier=carrier_user.carrier, carrier_user=carrier_user)
                raise NotFound("you are already yourself as a driver for this carrier.")
            except CarrierDriver.DoesNotExist:
                is_carrier_yourself_as_a_driver = carrier_user

        else:
            is_carrier_yourself_as_a_driver = None

        # Crate Driver for Carrier association
        carrier_driver = CarrierDriver(
            carrier=carrier_user.carrier,
            vehicle=vehicle,
            license_number=validated_data.get("license_number"),
            active=validated_data.get("active", True),
            price_visibility=validated_data.get("price_visibility", True),
            commision_percentage=validated_data.get("commision_percentage"),
            automatic_calculations=validated_data.get("automatic_calculations", False),
            is_owner_operator=validated_data.get("is_owner_operator", False),
            can_manage_load=validated_data.get("can_manage_load", False),
            can_reject_load=validated_data.get("can_reject_load", False),
            driver=driver,
            carrier_user=is_carrier_yourself_as_a_driver,
        )

        carrier_driver.save()

        # create account in stripe
        # account = StripeClient.create_account(
        #     type="custom",
        #     country="US",
        #     email=user.email,
        #     capabilities={
        #         "card_payments": {"requested": True},
        #         "transfers": {"requested": True},
        #     },
        #     tos_acceptance={"date": 1609798905, "ip": "8.8.8.8"},
        # )

        # if account and account.get("id", None):
        #     user.stripe_customer_id = account.get("id")
        #     user.save()

        return driver


class VehicleTypeSerializer(BaseModelSerializer):

    """Vehicle type Serializer"""

    class Meta:
        model = Vehicle
        fields = ("vehicle_year", "vehicle_make", "vehicle_model")


class VehicleLicencePlateSeriaizer(BaseModelSerializer):

    """Information Of Vehicle license plat number"""

    class Meta:
        model = Vehicle
        fields = ("state", "number")


class VehicleSerializer(BaseModelSerializer):

    """Vehicle Response Serializer"""

    type = serializers.SerializerMethodField()
    license_plate_number = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = ["id", "type", "license_plate_number"]

    def get_type(self, obj):
        return VehicleTypeSerializer(obj).data

    def get_license_plate_number(self, obj):
        return VehicleLicencePlateSeriaizer(obj).data


class DriverSerializer(BaseModelSerializer):

    """Driver Response Serializer"""

    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    price_visibility = serializers.SerializerMethodField()
    vehicle = serializers.SerializerMethodField()
    automatic_calculations = serializers.SerializerMethodField()
    commision_percentage = serializers.SerializerMethodField()
    can_manage_load = serializers.SerializerMethodField()
    can_reject_load = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()

    class Meta:
        model = Driver
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "phone",
            "email",
            "available",
            "price_visibility",
            "vehicle",
            "automatic_calculations",
            "commision_percentage",
            "can_manage_load",
            "can_reject_load",
            "active",
        ]

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_username(self, obj):
        return obj.user.username

    def get_phone(self, obj):
        return obj.user.phone

    def get_email(self, obj):
        return obj.user.email

    def get_available(self, obj):
        return obj.available

    def get_vehicle(self, obj):
        try:
            vehicle = CarrierDriver.objects.get(driver=obj)
            driver_vehicle = Vehicle.objects.get(id=vehicle.vehicle.id)
        except Exception:
            return None
        return VehicleSerializer(driver_vehicle).data

    def get_price_visibility(self, obj):
        try:
            driver = CarrierDriver.objects.get(driver=obj)
        except Exception:
            return None
        return driver.price_visibility

    def get_automatic_calculations(self, obj):
        try:
            driver = CarrierDriver.objects.get(driver=obj)
        except Exception:
            return None
        return driver.automatic_calculations

    def get_commision_percentage(self, obj):
        try:
            driver = CarrierDriver.objects.get(driver=obj)
        except Exception:
            return None
        return driver.commision_percentage

    def get_can_manage_load(self, obj):
        try:
            driver = CarrierDriver.objects.get(driver=obj)
        except Exception:
            return None
        return driver.can_manage_load

    def get_can_reject_load(self, obj):
        try:
            driver = CarrierDriver.objects.get(driver=obj)
        except Exception:
            return None
        return driver.can_reject_load

    def get_active(self, obj):
        try:
            driver = CarrierDriver.objects.get(driver=obj)
        except Exception:
            return None
        return driver.active


class DriverUpdateSerializer(BaseModelSerializer):

    """Driver Information Update Serializer"""

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    phone = serializers.CharField()
    password = serializers.CharField()
    available = serializers.BooleanField(required=True)
    t_shirt_size = serializers.CharField()
    license_number = serializers.CharField()
    active = serializers.BooleanField(required=True)
    price_visibility = serializers.BooleanField(required=True)
    commision_percentage = serializers.CharField()
    automatic_calculations = serializers.BooleanField(required=True)
    is_owner_operator = serializers.BooleanField(required=True)
    can_manage_load = serializers.BooleanField(required=True)
    can_reject_load = serializers.BooleanField(required=False)

    class Meta:
        model = Driver
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "password",
            "phone",
            "available",
            "t_shirt_size",
            "license_number",
            "active",
            "price_visibility",
            "commision_percentage",
            "automatic_calculations",
            "is_owner_operator",
            "can_manage_load",
            "can_reject_load",
        ]

    def validate_username(self, value):
        users = User.objects.filter(username=value)

        if self.instance:
            users = users.exclude(pk=self.instance.user.pk)

        if users:
            raise serializers.ValidationError("User is alreday exist with this username.")
        return value

    def validate_phone(self, value):
        users = User.objects.filter(phone=value)

        if self.instance:
            users = users.exclude(pk=self.instance.user.pk)

        if users:
            raise serializers.ValidationError("User is alreday exist with this phone.")
        return value

    def update(self, instance, validated_data):

        # Update Driver
        driver = User.objects.get(id=instance.user.id)
        driver.first_name = validated_data.get("first_name")
        driver.last_name = validated_data.get("last_name")
        driver.username = validated_data.get("username")
        driver.phone = validated_data.get("phone")
        driver.password = validated_data.get("password")
        driver.save()

        instance.available = validated_data.get("available")
        instance.t_shirt_size = validated_data.get("t_shirt_size")
        instance.save()

        # Update Carrier and Driver association
        carrier_driver = CarrierDriver.objects.get(driver=instance)
        carrier_driver.license_number = validated_data.get("license_number")
        carrier_driver.active = validated_data.get("active")
        carrier_driver.price_visibility = validated_data.get("price_visibility")
        carrier_driver.commision_percentage = validated_data.get("commision_percentage")
        carrier_driver.automatic_calculations = validated_data.get("automatic_calculations")
        carrier_driver.is_owner_operator = validated_data.get("is_owner_operator")
        carrier_driver.can_manage_load = validated_data.get("can_manage_load")
        carrier_driver.can_reject_load = validated_data.get("can_reject_load")
        carrier_driver.save()
        return instance


class DriverInformationSerializer(BaseModelSerializer):

    """Driver's Information"""

    class Meta:
        model = Driver
        fields = "__all__"


class DriverGeolocationUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = DriverCurrentLocation
        fields = (
            "id",
            "driver",
            "latitude",
            "longitude",
            "street",
            "city",
            "state",
            "country",
        )
