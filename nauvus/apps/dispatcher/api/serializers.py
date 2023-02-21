from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from nauvus.api.serializers import BaseModelSerializer, BaseSerializer
from nauvus.apps.carrier.models import Carrier, CarrierDispatcher, CarrierUser
from nauvus.apps.dispatcher.models import (
    Dispatcher,
    DispatcherInvitation,
    DispatcherReference,
    DispatcherServiceAgreement,
    DispatcherUser,
    DispatcherW9Information,
)
from nauvus.auth.api.serializers import AddressSerializer, UserSerializer
from nauvus.users.models import Address

User = get_user_model()


class DispatcherW9InformationSerializer(BaseModelSerializer):

    """Dispatcher w9 form information"""

    class Meta:
        model = DispatcherW9Information
        fields = ["id", "w9_document", "taxpayer_id_number"]
        read_only_fields = ["id"]


class DispatcherReferenceSerializer(BaseModelSerializer):

    """Dispatcher Reference Serializer"""

    class Meta:
        model = DispatcherReference
        fields = ["id", "company_name", "driver_name", "email", "phone"]
        read_only_fields = ["id"]


class DispatcherOrganizationInformationSerializer(BaseModelSerializer):

    """Dispatcher Organization Information Serializer"""

    class Meta:
        model = DispatcherUser
        exclude = ("uid", "created_at", "updated_at")


class DispatcherUserSerializer(BaseModelSerializer):

    """Dispatcher User's Information"""

    id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    class Meta:
        model = DispatcherUser
        fields = (
            "id",
            "email",
            "phone",
            "first_name",
            "last_name",
            "access_type",
            "is_owner",
        )

    def get_id(self, obj):
        return obj.id

    def get_email(self, obj):
        if hasattr(obj, "user"):
            return obj.user.email
        return None

    def get_phone(self, obj):
        if hasattr(obj, "user"):
            return obj.user.phone
        return None

    def get_first_name(self, obj):
        if hasattr(obj, "user"):
            return obj.user.first_name
        return None

    def get_last_name(self, obj):
        if hasattr(obj, "user"):
            return obj.user.last_name
        return None


class DispatcherOrganizationSerializer(BaseModelSerializer):

    """Dispatcher Organization Information"""

    # address = serializers.SerializerMethodField()
    # users = serializers.SerializerMethodField()
    total_users = serializers.SerializerMethodField()

    class Meta:
        model = Dispatcher
        fields = (
            "id",
            "organization_name",
            # "address",
            # "users",
            "total_users",
        )

    # def get_address(self, obj):
    #     dispatcher_user = DispatcherUser.objects.filter(
    #         dispatcher=obj, is_owner=True
    #     ).first()
    #     user_adress = Address.objects.filter(user=dispatcher_user.user).first()
    #     if user_adress:
    #         return AddressSerializer(user_adress).data
    #     return None

    # def get_users(self, obj):
    #     dispatcher_users = DispatcherUser.objects.filter(dispatcher=obj)
    #     if dispatcher_users:
    #         return DispatcherUserSerializer(dispatcher_users, many=True).data
    #     return None

    def get_total_users(self, obj):
        dispatcher_users = DispatcherUser.objects.filter(
            dispatcher=obj
        ).count()
        return dispatcher_users


class DispatcherOrganizationUpdateSerializer(BaseModelSerializer):

    """Update the Email and Phone For Dispatcher Organization"""

    email = serializers.EmailField()
    phone = serializers.CharField()

    class Meta:
        model = Dispatcher
        fields = ["email", "phone"]

    def validate_email(self, value):
        users = User.objects.filter(email=value)

        if self.instance:
            dispatcher_user = DispatcherUser.objects.get(
                dispatcher=self.instance, is_owner=True
            )
            users = users.exclude(pk=dispatcher_user.user.id)
        if users:
            raise serializers.ValidationError(
                "User is alreday exist with this email."
            )
        return value

    def validate_phone(self, value):
        users = User.objects.filter(phone=value)

        if self.instance:
            dispatcher_user = DispatcherUser.objects.get(
                dispatcher=self.instance, is_owner=True
            )
            users = users.exclude(pk=dispatcher_user.user.id)
        if users:
            raise serializers.ValidationError(
                "User is alreday exist with this phone."
            )
        return value

    def update(self, instance, validated_data):
        dispatcher = Dispatcher.objects.get(id=instance.id)
        dispatcher_user = DispatcherUser.objects.get(
            dispatcher=dispatcher, is_owner=True
        )
        user = User.objects.get(id=dispatcher_user.user.id)
        user.email = validated_data.get("email")
        user.phone = validated_data.get("phone")
        user.save()
        return instance


class DispatcherOnbordingStatusSerializer(BaseModelSerializer):

    """Dispatcher Onboarding Status Serializer"""

    w9_information = serializers.SerializerMethodField()
    reference = serializers.SerializerMethodField()
    service_agreement = serializers.SerializerMethodField()

    class Meta:
        model = Dispatcher
        fields = ("reference", "w9_information", "service_agreement")

    def get_reference(status, obj):
        if DispatcherReference.objects.filter(dispatcher=obj.dispatcher):
            return True
        return False

    def get_w9_information(status, obj):
        if DispatcherW9Information.objects.filter(dispatcher=obj.dispatcher):
            return True
        return False

    def get_service_agreement(self, obj):
        service_agreement = DispatcherServiceAgreement.objects.filter(
            dispatcher=obj.dispatcher
        ).first()
        if service_agreement and service_agreement.is_signed:
            return True
        return False


class DispatcherOnbordingSerializer(BaseSerializer):

    """Dispatcher Onboarding Serializer"""

    status = serializers.SerializerMethodField()

    class Meta:
        model = Dispatcher
        fields = ["id", "status"]

    def get_status(self, obj):
        return DispatcherOnbordingStatusSerializer(obj).data


class DispatcherInvitationCreateSerializer(BaseModelSerializer):

    """Invite Dispatcher User's"""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "user_type")

    def create(self, validated_data):
        request = self.context.get("request")
        # create user
        user = User(
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            email=validated_data.get("email"),
            phone=validated_data.get("phone"),
            user_type=User.DISPATCHER,
        )
        user.save()

        # create Invited dispatcher
        try:
            dispatcher_user = DispatcherUser.objects.filter(
                user=request.user
            ).first()
        except DispatcherUser.DoesNotExist:
            raise NotFound("Dispatcher Not Found.")

        invited_dispatcher = DispatcherInvitation(
            user=user,
            dispatcher=dispatcher_user.dispatcher,
            active=request.data.get("active"),
            commision=request.data.get("commision"),
        )
        invited_dispatcher.save()

        return user


class DispatcherInvitationUserSerializer(BaseModelSerializer):

    """Dispatcher User's Response Serializer"""

    id = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    commision = serializers.SerializerMethodField()

    class Meta:
        model = DispatcherInvitation
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "active",
            "organization_name",
            "commision",
        )

    def get_id(self, obj):
        return obj.id

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_email(self, obj):
        return obj.user.email

    def get_phone(self, obj):
        return obj.user.phone

    def get_active(self, obj):
        return obj.active

    def get_organization_name(self, obj):
        return obj.dispatcher.organization_name

    def get_commision(self, obj):
        return obj.commision


class DispatcherInvitationInformationSerializer(BaseModelSerializer):

    """Serializer for the Invited Dispatcher"""

    class Meta:
        model = DispatcherInvitation
        fields = "__all__"


class DispatcherAdminInvitationCreateSerializer(BaseModelSerializer):

    """Invite Dispatcher Admin For the Dispatcher Organization"""

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
        )

    def create(self, validated_data):
        request = self.context.get("request")

        # create user
        user = User(
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            email=validated_data.get("email"),
            user_type=User.DISPATCHER,
        )
        user.save()

        # create dispatcher admin
        dispatcher_user = DispatcherUser.objects.get(user=request.user)
        invited_dispatcher_admin = DispatcherUser(
            user=user,
            dispatcher=dispatcher_user.dispatcher,
            permission=request.data.get("permission"),
        )
        invited_dispatcher_admin.save()

        return user


class DispatcherAdminInvitationUserSerializer(BaseModelSerializer):

    """Dispatcher Admin Invitation Information Serializer."""

    id = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    permission = serializers.SerializerMethodField()
    pending_invitation = serializers.SerializerMethodField()

    class Meta:
        model = DispatcherUser
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "permission",
            "pending_invitation",
        )

    def get_id(self, obj):
        return obj.id

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_email(self, obj):
        return obj.user.email

    def get_permission(self, obj):
        return obj.permission

    def get_pending_invitation(self, obj):
        return obj.pending_invitation


class DispatcherAdminInvitationInformationSerializer(BaseModelSerializer):

    """Dispatcher Admin Invitation Information Serializer."""

    user = serializers.SerializerMethodField()

    class Meta:
        model = DispatcherUser
        fields = (
            "id",
            "is_owner",
            "access_type",
            "is_current_organization",
            "pending_invitation",
            "user",
            "dispatcher",
        )

    def get_user(self, obj):
        return UserSerializer(obj.user).data


class CurrentDispatcherOrganizationInformationSerializer(BaseModelSerializer):

    """Current Organization Information For the Dispatcher User"""

    class Meta:
        model = DispatcherUser
        fields = "__all__"


class CarrierUserInformationSerializer(BaseModelSerializer):

    """Current Organization Information Serializer"""

    class Meta:
        model = User
        fields = (
            "first_name",
            "email",
            "phone",
        )


class CarrierInformationSerializer(BaseModelSerializer):

    """Carrier Response Serializer with address"""

    address = serializers.SerializerMethodField()

    class Meta:
        model = Carrier
        fields = ("id", "organization_name", "address")

    def get_address(self, obj):
        carrier_user = CarrierUser.objects.filter(
            carrier=obj, is_owner=True
        ).first()
        address = Address.objects.filter(user=carrier_user.user).first()
        return AddressSerializer(address).data


class DispatcherCarrierSerializer(BaseModelSerializer):

    """Information Of Associated Carriers for the Dispatcher Organization"""

    carrier = serializers.SerializerMethodField()

    class Meta:
        model = Dispatcher
        fields = ("carrier",)

    def get_carrier(self, obj):
        dispatcher_carrier = CarrierDispatcher.objects.filter(
            dispatcher__id=obj.id
        ).values_list("carrier__id")
        carriers = Carrier.objects.filter(id__in=dispatcher_carrier)
        return CarrierInformationSerializer(carriers, many=True).data


class DispatcherOwnerSerializer(BaseModelSerializer):

    """Dispatcher Owner Information Serializer"""

    user = serializers.SerializerMethodField()

    class Meta:
        model = Dispatcher
        fields = (
            "id",
            "source",
            "amount_of_experience",
            # "driver_type",
            # "driver_or_carrier_to_onboard",
            "organization_name",
            "number_of_dispatcher",
            "no_of_drivers",
            "user",
        )

    def get_user(self, obj):
        dispatcher_user = DispatcherUser.objects.filter(
            dispatcher=obj, is_owner=True
        ).first()
        if dispatcher_user:
            return UserSerializer(dispatcher_user.user).data
        else:
            return None


class DispatcherCarrierInformationSerializer(BaseModelSerializer):

    """Dispatcher Information For the Carrier Organizetion"""

    # carrier = serializers.SerializerMethodField()
    carrier_id = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    mc_number = serializers.SerializerMethodField()
    dot_number = serializers.SerializerMethodField()

    class Meta:
        model = CarrierDispatcher
        fields = (
            "id",
            "active",
            "carrier_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "organization_name",
            "mc_number",
            "dot_number",
        )

    # def get_carrier(self, obj):
    #     return CarrierSerializer(obj.carrier).data

    def get_carrier_id(self, obj):
        if obj.carrier:
            return obj.carrier.id
        else:
            return None

    def get_first_name(self, obj):
        if obj.carrier:
            carrier_user = CarrierUser.objects.filter(
                carrier=obj.carrier, is_owner=True
            ).first()
            if carrier_user:
                return carrier_user.user.first_name
            else:
                return None
        else:
            return None

    def get_last_name(self, obj):
        if obj.carrier:
            carrier_user = CarrierUser.objects.filter(
                carrier=obj.carrier, is_owner=True
            ).first()
            if carrier_user:
                return carrier_user.user.last_name
            else:
                return None
        else:
            return None

    def get_email(self, obj):
        if obj.carrier:
            carrier_user = CarrierUser.objects.filter(
                carrier=obj.carrier, is_owner=True
            ).first()
            if carrier_user:
                return carrier_user.user.email
            else:
                return None
        else:
            return None

    def get_phone(self, obj):
        if obj.carrier:
            carrier_user = CarrierUser.objects.filter(
                carrier=obj.carrier, is_owner=True
            ).first()
            if carrier_user:
                return carrier_user.user.phone
            else:
                return None
        else:
            return None

    def get_organization_name(self, obj):
        if obj.carrier:
            return obj.carrier.organization_name
        else:
            return None

    def get_mc_number(self, obj):
        if obj.carrier:
            return obj.carrier.mc_number
        else:
            return None

    def get_dot_number(self, obj):
        if obj.carrier:
            return obj.carrier.dot_number
        else:
            return None


class DispatcherCarrierUpdateSerializer(BaseModelSerializer):

    active = serializers.BooleanField(required=True)

    class Meta:
        model = CarrierDispatcher
        fields = ("active",)

    def update(self, instance, validated_data):
        request = self.context.get("request")

        try:
            dispatcher_user = DispatcherUser.objects.get(
                user=request.user,
                is_current_organization=True,
            )
        except Exception:
            raise NotFound("Dispatcher User Not Found.")

        instance.active = validated_data.get("active")
        instance.save()

        return instance


class CurrentDispatcherSerializer(BaseModelSerializer):

    address = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    dispatcher_id = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    class Meta:
        model = Carrier
        fields = (
            "dispatcher_id",
            "organization_name",
            "address",
            "email",
            "phone",
            "documents",
        )

    def get_dispatcher_id(self, obj):
        return obj.id

    def get_address(self, obj):
        dispatcher_user = DispatcherUser.objects.filter(
            dispatcher=obj, is_owner=True
        ).first()
        user_adress = Address.objects.filter(user=dispatcher_user.user).first()
        if user_adress:
            return AddressSerializer(user_adress).data
        return {}

    def get_email(self, obj):
        dispatcher_user = DispatcherUser.objects.filter(
            dispatcher=obj, is_owner=True
        ).first()
        if dispatcher_user:
            return dispatcher_user.user.email
        else:
            return None

    def get_phone(self, obj):
        dispatcher_user = DispatcherUser.objects.filter(
            dispatcher=obj, is_owner=True
        ).first()
        if dispatcher_user:
            return dispatcher_user.user.phone
        else:
            return None

    def get_documents(self, obj):
        w9_information = DispatcherW9Information.objects.filter(
            dispatcher=obj
        ).first()
        data = {
            "w9_information": DispatcherW9InformationSerializer(
                w9_information
            ).data,
        }
        return data
