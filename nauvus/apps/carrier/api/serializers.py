from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from nauvus.api.serializers import BaseModelSerializer, BaseSerializer
from nauvus.apps.carrier.models import (
    Carrier,
    CarrierBroker,
    CarrierDispatcher,
    CarrierFleetApplication,
    CarrierServiceAgreement,
    CarrierTrailerSize,
    CarrierTrailerType,
    CarrierUser,
    CarrierW9Information,
)
from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.apps.driver.models import CarrierDriver
from nauvus.auth.api.serializers import AddressSerializer
from nauvus.users.models import Address

User = get_user_model()


class CarrierBrokerSerializer(BaseModelSerializer):

    """Carrier's Broker Information Serializer"""

    broker_name = serializers.SerializerMethodField()

    class Meta:
        model = CarrierBroker
        fields = (
            "id",
            "broker_name",
            "username",
            "password",
        )

    def get_broker_name(self, obj):
        if hasattr(obj, "broker"):
            return obj.broker.name
        return None


class CarrierBrokerCreateSerializer(BaseModelSerializer):

    """Carrier's Broker Information Serializer"""

    class Meta:
        model = CarrierBroker
        fields = ("id", "carrier", "broker", "username", "password")


class CarrierFleetApplicationSerializer(BaseModelSerializer):

    """Carrier Fleet Application Serializer"""

    class Meta:
        model = CarrierFleetApplication
        exclude = ("carrier", "created_at", "updated_at", "uid")


class CarrierW9InformationSerializer(BaseModelSerializer):

    """Carrier W9 Form For Carrier Onboarding."""

    class Meta:
        model = CarrierW9Information
        exclude = ("carrier", "created_at", "updated_at", "uid")


class CarrierOrganizationUpdateSerializer(BaseSerializer):

    """Update the Email and Phone For the Carrier Organization"""

    email = serializers.EmailField()
    phone = serializers.CharField()

    class Meta:
        model = Carrier
        fields = ["email", "phone"]

    def validate_email(self, value):
        users = User.objects.filter(email=value)

        if self.instance:
            carrier_user = CarrierUser.objects.get(carrier=self.instance, is_owner=True)
            users = users.exclude(pk=carrier_user.user.id)
        if users:
            raise serializers.ValidationError("User is alreday exist with this email.")
        return value

    def validate_phone(self, value):
        users = User.objects.filter(phone=value)

        if self.instance:
            carrier_user = CarrierUser.objects.get(carrier=self.instance, is_owner=True)
            users = users.exclude(pk=carrier_user.user.id)
        if users:
            raise serializers.ValidationError("User is alreday exist with this phone.")
        return value

    def update(self, instance, validated_data):
        carrier = Carrier.objects.get(id=instance.id)
        carrier_user = CarrierUser.objects.get(carrier=carrier, is_owner=True)
        user = User.objects.get(id=carrier_user.user.id)
        user.email = validated_data.get("email")
        user.phone = validated_data.get("phone")
        user.save()
        return instance


class CarrierUserSerializer(BaseModelSerializer):

    """Carrier User Response Serializer"""

    # id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    # access_type = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    class Meta:
        model = CarrierUser
        fields = (
            "id",
            "email",
            "phone",
            "first_name",
            "last_name",
            "access_type",
            "is_owner",
        )

    # def get_id(self, obj):
    #     return obj.id

    def get_email(self, obj):
        if obj.user:
            return obj.user.email
        return None

    def get_phone(self, obj):
        return obj.user.phone
        return None

    def get_first_name(self, obj):
        if obj.user:
            return obj.user.first_name
        return None

    def get_last_name(self, obj):
        if obj.user:
            return obj.user.last_name
        return None

    # def get_access_type(self, obj):
    #     return obj.access_type


class CarrierOrganizationSerializer(BaseModelSerializer):

    """Carrier Oraganization Information Serializer"""

    # address = serializers.SerializerMethodField()
    total_users = serializers.SerializerMethodField()
    # users = serializers.SerializerMethodField()
    # broker = serializers.SerializerMethodField()

    class Meta:
        model = Carrier
        fields = (
            "id",
            "organization_name",
            # "users",
            "total_users",
            # "address",
        )

    # def get_address(self, obj):
    #     carrier_user = CarrierUser.objects.filter(
    #         carrier=obj, is_owner=True
    #     ).first()
    #     user_adress = Address.objects.filter(user=carrier_user.user).first()
    #     if user_adress:
    #         return AddressSerializer(user_adress).data
    #     return None

    # def get_users(self, obj):
    #     carrier_users = CarrierUser.objects.filter(carrier=obj)
    #     if carrier_users:
    #         return CarrierUserSerializer(carrier_users, many=True).data
    #     return None

    # def get_broker(self, obj):
    #     carrier_broker = CarrierBroker.objects.filter(carrier=obj.id)
    #     if carrier_broker:
    #         return CarrierBrokerSerializer(carrier_broker, many=True).data
    #     return None

    def get_total_users(self, obj):
        carrier_users_count = CarrierUser.objects.filter(carrier=obj).count()
        return carrier_users_count


class CarrierOnboardingStatusSerializer(BaseModelSerializer):

    """Onboarding Status Of Carrier Organization."""

    fleet_application = serializers.SerializerMethodField()
    w9_information = serializers.SerializerMethodField()
    # broker_setup = serializers.SerializerMethodField()
    service_agreement = serializers.SerializerMethodField()

    class Meta:
        model = Carrier
        fields = (
            "fleet_application",
            "w9_information",
            # "broker_setup",
            "service_agreement",
        )

    def get_fleet_application(status, obj):
        if CarrierFleetApplication.objects.filter(carrier=obj.carrier):
            return True
        return False

    # TODO: Discard if broker service deprecated
    # def get_broker_setup(status, obj):
    #     if CarrierBroker.objects.filter(carrier=obj.carrier):
    #         return True
    #     return False

    def get_w9_information(status, obj):
        if CarrierW9Information.objects.filter(carrier=obj.carrier):
            return True
        return False

    def get_service_agreement(self, obj):
        service_agreement = CarrierServiceAgreement.objects.filter(carrier=obj.carrier).first()
        if service_agreement and service_agreement.is_signed:
            return True
        return False


class CarrierOnboardingStatusResultSerializer(BaseModelSerializer):

    """Carrier Onboarding Status Responser Serializer"""

    status = serializers.SerializerMethodField()
    # onboarding = serializers.SerializerMethodField()

    class Meta:
        model = Carrier
        fields = ("id", "status")

    def get_status(self, obj):
        return CarrierOnboardingStatusSerializer(obj).data

    # def get_onboarding(self, obj):
    #     if not CarrierFleetApplication.objects.filter(carrier=obj.carrier):
    #         return "on-going"
    #     if not CarrierBroker.objects.filter(carrier=obj.carrier):
    #         return "on-going"
    #     if not CarrierW9Information.objects.filter(carrier=obj.carrier):
    #         return "on-going"

    #     return "completed"


class CarrierDispatcherCreateSerializer(BaseModelSerializer):

    """Invite the Dispatcher For the Carrier Organization."""

    class Meta:
        model = CarrierDispatcher
        exclude = ("uid", "created_at", "updated_at", "user")

    def create(self, validated_data):
        request = self.context.get("request")

        # create carrier dispatcher
        try:
            carrier_user = CarrierUser.objects.get(user=request.user)
        except Exception:
            raise NotFound("Carrier Not Found.")

        try:
            dispatcher = Dispatcher.objects.get(id=request.data.get("dispatcher"))
        except Exception:
            raise NotFound("Dispatcher not Found")

        existed_carrier_dispatcher = CarrierDispatcher.objects.filter(carrier=carrier_user.carrier, active=True)

        carrier_dispatcher = CarrierDispatcher(
            carrier=carrier_user.carrier,
            dispatcher=dispatcher,
            active=validated_data.get("active"),
        )

        if existed_carrier_dispatcher:
            raise NotFound("More than one dispatcher not allowed.")
        else:
            carrier_dispatcher.save()

        return carrier_dispatcher


class CarrierDispatcherUpdateSerializer(BaseModelSerializer):

    active = serializers.BooleanField(required=True)

    class Meta:
        model = CarrierDispatcher
        fields = ("active",)

    def update(self, instance, validated_data):
        request = self.context.get("request")

        try:
            carrier_user = CarrierUser.objects.get(
                user=request.user,
                is_current_organization=True,
            )
        except Exception:
            raise NotFound("Carrier Not Found.")

        carrier_dispatcher = CarrierDispatcher.objects.filter(carrier=carrier_user.carrier).exclude(id=instance.id)
        carrier_dispatcher.update(active=False)

        instance.active = validated_data.get("active")
        instance.save()

        return instance


class CarrierDispatcherInformationSerializer(BaseModelSerializer):

    """Dispatcher Information For the Carrier Organizetion"""

    # carrier = serializers.SerializerMethodField()
    dispatcher_id = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()

    class Meta:
        model = CarrierDispatcher
        fields = (
            "id",
            "active",
            "dispatcher_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "organization_name",
        )

    # def get_carrier(self, obj):
    #     return CarrierSerializer(obj.carrier).data

    def get_dispatcher_id(self, obj):
        if obj.dispatcher:
            return obj.dispatcher.id
        else:
            return None

    def get_first_name(self, obj):
        if obj.dispatcher:
            dispatcher_user = DispatcherUser.objects.filter(dispatcher=obj.dispatcher, is_owner=True).first()
            if dispatcher_user:
                return dispatcher_user.user.first_name
            else:
                return None
        else:
            return None

    def get_last_name(self, obj):
        if obj.dispatcher:
            dispatcher_user = DispatcherUser.objects.filter(dispatcher=obj.dispatcher, is_owner=True).first()
            if dispatcher_user:
                return dispatcher_user.user.last_name
            else:
                return None
        else:
            return None

    def get_email(self, obj):
        if obj.dispatcher:
            dispatcher_user = DispatcherUser.objects.filter(dispatcher=obj.dispatcher, is_owner=True).first()
            if dispatcher_user:
                return dispatcher_user.user.email
            else:
                return None
        else:
            return None

    def get_phone(self, obj):
        if obj.dispatcher:
            dispatcher_user = DispatcherUser.objects.filter(dispatcher=obj.dispatcher, is_owner=True).first()
            if dispatcher_user:
                return dispatcher_user.user.phone
            else:
                return None
        else:
            return None

    def get_organization_name(self, obj):
        if obj.dispatcher:
            return obj.dispatcher.organization_name
        else:
            return None


class CurrentCarrierOrganizationInformationSerializer(BaseModelSerializer):

    """Change Organization For the Carrier User's"""

    class Meta:
        model = CarrierUser
        fields = "__all__"


class CarrierResponseSerializer(BaseModelSerializer):

    """Response For Carrier's Information with address."""

    address = serializers.SerializerMethodField()

    class Meta:
        model = Carrier
        fields = ("id", "organization_name", "address")

    def get_address(self, obj):
        carrier_user = CarrierUser.objects.filter(carrier=obj, is_owner=True).first()
        user_adress = Address.objects.filter(user=carrier_user.user).first()
        if user_adress:
            return AddressSerializer(user_adress).data
        return None


class CurrentCarrierSerializer(BaseModelSerializer):

    address = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    carrier_id = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    # connected_brokers = serializers.SerializerMethodField()
    total_drivers = serializers.SerializerMethodField()

    class Meta:
        model = Carrier
        fields = (
            "carrier_id",
            "organization_name",
            "mc_number",
            "dot_number",
            "fleet_id",
            "address",
            "email",
            "first_name",
            "last_name",
            "phone",
            "documents",
            # "connected_brokers",
            "total_drivers",
        )

    def get_carrier_id(self, obj):
        return obj.id

    def get_address(self, obj):
        carrier_user = CarrierUser.objects.filter(carrier=obj, is_owner=True).first()
        user_adress = Address.objects.filter(user=carrier_user.user).first()
        if user_adress:
            return AddressSerializer(user_adress).data
        return {}

    def get_email(self, obj):
        carrier_user = CarrierUser.objects.filter(carrier=obj, is_owner=True).first()
        if carrier_user:
            return carrier_user.user.email
        else:
            return None

    def get_phone(self, obj):
        carrier_user = CarrierUser.objects.filter(carrier=obj, is_owner=True).first()
        if carrier_user:
            return carrier_user.user.phone
        else:
            return None

    def get_first_name(self, obj):
        carrier_user = CarrierUser.objects.filter(carrier=obj, is_owner=True).first()
        if carrier_user:
            return carrier_user.user.first_name
        else:
            return None

    def get_last_name(self, obj):
        carrier_user = CarrierUser.objects.filter(carrier=obj, is_owner=True).first()
        if carrier_user:
            return carrier_user.user.last_name
        else:
            return None

    def get_documents(self, obj):
        fleet_application = CarrierFleetApplication.objects.filter(carrier=obj).first()
        w9_information = CarrierW9Information.objects.filter(carrier=obj).first()
        data = {
            "fleet_application": CarrierFleetApplicationSerializer(fleet_application).data,
            "w9_information": CarrierW9InformationSerializer(w9_information).data,
        }
        return data

    # def get_connected_brokers(self, obj):
    #     carrier_brokers = CarrierBroker.objects.filter(carrier=obj)
    #     return CarrierBrokerSerializer(carrier_brokers, many=True).data

    def get_total_drivers(self, obj):
        carrier_drivers = CarrierDriver.objects.filter(carrier=obj).count()
        return carrier_drivers


class CarrierTrailerTypeSerializer(BaseModelSerializer):
    class Meta:
        model = CarrierTrailerType
        fields = ("id", "trailer_type")


class CarrierTrailerSizeSerializer(BaseModelSerializer):
    class Meta:
        model = CarrierTrailerSize
        fields = ("id", "trailer_size")


class SendDocumentSerializer(BaseSerializer):

    email = serializers.EmailField(required=True)
    documents = serializers.ListField()
