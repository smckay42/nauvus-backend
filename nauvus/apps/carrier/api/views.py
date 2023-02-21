import random

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from nauvus.api.permissions import CarrierHasPermission, IsCarrier
from nauvus.api.viewsets import BaseCreateViewSet, BaseModelViewSet
from nauvus.apps.carrier.models import Carrier, CarrierBroker, CarrierDispatcher, CarrierUser
from nauvus.apps.driver.api.serializer import DriverInformationSerializer
from nauvus.apps.driver.models import CarrierDriver, Driver
from nauvus.apps.vehicle.api.serializers import VehicleInformationSerializer
from nauvus.apps.vehicle.models import Vehicle
from nauvus.auth.api.serializers import EmailUpdateOtpVerfySerializer, PasswordOtpGenerateSerializer
from nauvus.auth.tasks import send_documents, send_password_reset_mail
from nauvus.users.models import EmailUpdateOtpVerification

from .serializers import (
    CarrierBrokerCreateSerializer,
    CarrierBrokerSerializer,
    CarrierDispatcherCreateSerializer,
    CarrierDispatcherInformationSerializer,
    CarrierDispatcherUpdateSerializer,
    CarrierFleetApplicationSerializer,
    CarrierOnboardingStatusResultSerializer,
    CarrierOrganizationSerializer,
    CarrierOrganizationUpdateSerializer,
    CarrierUserSerializer,
    CarrierW9InformationSerializer,
    CurrentCarrierOrganizationInformationSerializer,
    CurrentCarrierSerializer,
    SendDocumentSerializer,
)

User = get_user_model()


class CarrierFleetApplicationViewset(BaseCreateViewSet):

    """
    create:
        Upload Fleet Application.

    update:
        Upload Fleet Application.

    destroy:
        Delete Fleet Application.
    """

    serializer_class = CarrierFleetApplicationSerializer

    permission_classes = [IsAuthenticated, IsCarrier]

    def create(self, request):

        try:
            carrier_object = CarrierUser.objects.get(user=request.user)
        except Exception:
            raise NotFound("Carrier not found")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        carrier_fleet_application = serializer.save()
        carrier_fleet_application.carrier = carrier_object.carrier
        carrier_fleet_application.save()
        return Response(CarrierFleetApplicationSerializer(carrier_fleet_application).data)


class CarrierBrokerCreateViewset(ModelViewSet):

    """
    create:
        create the broker.

    update:
        Update broker.

    retrieve:
        Get broker.

    list:
        List of broker

    destroy:
        Delete broker.

    """

    serializer_class = CarrierBrokerSerializer

    permission_classes = [IsAuthenticated, IsCarrier]

    ordering_fields = (
        "id",
        "broker__id",
        "broker__name",
        "username",
        "created_at",
        "updated_at",
    )

    def get_queryset(self):
        carrier_user = CarrierUser.objects.filter(user=self.request.user, is_current_organization=True).first()
        broker = CarrierBroker.objects.filter(carrier=carrier_user.carrier)
        return broker

    def get_serializer_class(self):
        actions = {
            "create": CarrierBrokerCreateSerializer,
            "update": CarrierBrokerSerializer,
            "retrieve": CarrierBrokerSerializer,
            "list": CarrierBrokerSerializer,
        }
        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def create(self, request):
        try:
            carrier = CarrierUser.objects.get(user=request.user, is_current_organization=True)
        except Exception:
            raise NotFound("Carrier not found")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        carrier_broker = serializer.save()

        carrier_broker.carrier = carrier.carrier
        carrier_broker.save()

        return Response(CarrierBrokerSerializer(carrier_broker).data)

    def update(self, request, pk=None):

        try:
            carrier_brokers = self.get_queryset()
            carrier_broker = carrier_brokers.get(id=pk)
        except Exception:
            raise NotFound("Carrier-Broker not found")

        serializer = self.get_serializer(carrier_broker, data=request.data)
        serializer.is_valid(raise_exception=True)
        carrier_broker = serializer.save()

        # carrier_broker.carrier = carrier
        # carrier_broker.save()

        return Response(CarrierBrokerSerializer(carrier_broker).data)

    # def retrieve(self, request, pk=None):

    #     try:
    #         carrier = CarrierBroker.objects.get(id=pk)
    #     except Exception:
    #         raise NotFound("Carrier-Broker not found")

    #     return Response(CarrierBrokerSerializer(carrier).data)


class CarrierW9InformationViewset(BaseCreateViewSet):

    """
    create:
        Upload w9 Form.

    update:
        Update w9 Form.

    destroy;
        Delete w9 Form.
    """

    serializer_class = CarrierW9InformationSerializer

    permission_classes = [IsAuthenticated, IsCarrier]

    def create(self, request):

        try:
            carrier = CarrierUser.objects.get(user=request.user)
        except Exception:
            raise NotFound("Carrier not found")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        w9_information = serializer.save()

        w9_information.carrier = carrier.carrier
        w9_information.save()
        return Response(CarrierW9InformationSerializer(w9_information).data)


class CarrierOrganizationViewset(BaseModelViewSet):

    """
    reset:
        Validate email and send otp for password reset.

    update:
        Verify otp in password reset process.
    """

    serializer_class = CarrierOrganizationSerializer

    permission_classes = [IsAuthenticated, IsCarrier]

    def get_queryset(self):
        if (
            self.request.user.user_type == User.CARRIER_OWNER
            or self.request.user.user_type == User.CARRIER_OWNER_OPERATOR
        ):
            carrier_users = CarrierUser.objects.filter(user=self.request.user).values_list("carrier__id")
            carriers = Carrier.objects.filter(id__in=carrier_users)
            return carriers
        else:
            raise NotFound("Permission Denied.")

    def get_serializer_class(self):
        actions = {
            "update": CarrierOrganizationUpdateSerializer,
            "reset": PasswordOtpGenerateSerializer,
        }

        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[AllowAny],
        url_path="reset",
    )
    def reset(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        try:
            email = User.objects.get(email=serializer.data["email"])

        except Exception:
            raise NotFound("User not found.")

        reset_key = "".join(random.choices("1234567890", k=4))  # noqa

        user = EmailUpdateOtpVerification(email=email, otp=reset_key)
        user.save()

        send_password_reset_mail(user.email, user.otp)
        response = self.get_serializer(user).data
        response["message"] = "Password reset key is sent to your email."
        return Response(response)

    def update(self, request, pk=None):

        serializer = EmailUpdateOtpVerfySerializer(data=request.data)
        serializer.is_valid()

        reset_key = serializer.data.get("otp")
        otp = EmailUpdateOtpVerification.objects.filter(otp=reset_key).first()

        try:
            if otp.otp != reset_key:
                raise serializers.ValidationError({"password_reset_key": "Provided password reset key is invalid."})
        except Exception:
            return None

        try:
            carrier = Carrier.objects.get(pk=pk)
        except Carrier.DoesNotExist:
            raise NotFound("Carrier Not found")

        serializer = self.get_serializer(carrier, data=request.data)
        serializer.is_valid(raise_exception=True)
        carrier = serializer.save()
        response = {}
        response["carrier"] = CarrierOrganizationSerializer(carrier).data
        return Response(response)


class CarrierOnboardingStatusView(APIView):

    permission_classes = [IsAuthenticated, IsCarrier]

    def get_object(self):
        carrier = CarrierUser.objects.filter(user=self.request.user).first()
        if not carrier:
            raise NotFound("Carrier not found")
        return carrier

    def get(self, request, pk=None):
        carrier = self.get_object()
        return Response(CarrierOnboardingStatusResultSerializer(carrier).data)


class CarrierDispatcherInvitationViewset(BaseModelViewSet):

    """
    create:
        Invite Carrier Dispatcher

    retrieve:
        Get Carrier Dispatcher

    update:
        Update Carrier Dispatcher

    destroy:
        Delete Carrier Dispatcher

    """

    serializer_class = CarrierDispatcherCreateSerializer

    permission_classes = [IsAuthenticated, IsCarrier]

    def get_queryset(self):
        status = self.request.GET.get("status")
        carrier_user = CarrierUser.objects.filter(user=self.request.user, is_current_organization=True).first()
        carrier_dispatcher = CarrierDispatcher.objects.filter(carrier=carrier_user.carrier)

        if status:
            if status == "active":
                carrier_dispatcher = carrier_dispatcher.filter(active=True)
            elif status == "inactive":
                carrier_dispatcher = carrier_dispatcher.filter(active=False)
            else:
                pass

        return carrier_dispatcher

    def get_serializer_class(self):
        actions = {
            "list": CarrierDispatcherInformationSerializer,
            "retrieve": CarrierDispatcherInformationSerializer,
            "update": CarrierDispatcherUpdateSerializer,
        }

        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def get_permissions(self):
        actions = {
            "update": [
                CarrierHasPermission,
            ],
            "delete": [
                CarrierHasPermission,
            ],
        }

        if self.action in actions:
            self.permission_classes += actions.get(self.action)

        return super().get_permissions()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        carrier_dispatcher = serializer.save()
        return Response(self.serializer_class(carrier_dispatcher).data)

    def update(self, request, pk):

        try:
            carrier_dispatchers = self.get_queryset()
            carrier_dispatcher = carrier_dispatchers.get(id=pk)
        except Exception:
            raise NotFound("Carrier Dispatcher NotFound.")

        serializer = self.get_serializer(carrier_dispatcher, data=request.data)
        serializer.is_valid(raise_exception=True)
        carrier_dispatcher = serializer.save()

        return Response(CarrierDispatcherInformationSerializer(carrier_dispatcher).data)


class CurrentCarrierOrganiztionViewset(BaseModelViewSet):

    """
    update_org:
        Carrier Current Organization Information.
    """

    serializer_class = CurrentCarrierOrganizationInformationSerializer

    permission_classes = [IsAuthenticated, IsCarrier]

    def get_queryset(self):
        try:
            carrier_user = CarrierUser.objects.get(user=self.request.user, is_current_organization=True)
        except Exception:
            raise NotFound("Current Carrier User Not Found.")
        return carrier_user.carrier

    def get_serializer_class(self):
        actions = {
            "list": CurrentCarrierSerializer,
            "update_org": CurrentCarrierOrganizationInformationSerializer,
            # "users": CarrierOrganizationSerializer,
            "users": CarrierUserSerializer,
            "send_documents": SendDocumentSerializer,
        }

        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def get_permissions(self):
        actions = {
            "list": [
                CarrierHasPermission,
            ],
            "update": [
                CarrierHasPermission,
            ],
            "users": [
                CarrierHasPermission,
            ],
            "send_documents": [
                CarrierHasPermission,
            ],
        }

        if self.action in actions:
            self.permission_classes += actions.get(self.action)

        return super().get_permissions()

    def list(self, request):
        carrier = self.get_queryset()
        return Response(self.get_serializer(carrier).data)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[IsAuthenticated, IsCarrier],
        url_path="update",
    )
    def update_org(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        carrier_organization = serializer.data

        carrier = CarrierUser.objects.filter(user=request.user, is_current_organization=True).first()

        carrier.is_current_organization = False
        carrier.save()

        try:
            current_carrier_user = CarrierUser.objects.get(user=request.user, carrier=carrier_organization["carrier"])
            current_carrier_user.is_current_organization = True
            current_carrier_user.save()
        except Exception:

            raise NotFound("Carrier Not Found")

        vehicle = Vehicle.objects.filter(carrier=current_carrier_user.carrier)
        carrier_driver = CarrierDriver.objects.filter(carrier=current_carrier_user.carrier).values_list("driver__id")
        driver = Driver.objects.filter(id__in=carrier_driver)

        response = {}
        response["carrier"] = CurrentCarrierOrganizationInformationSerializer(current_carrier_user).data
        response["vehicle"] = VehicleInformationSerializer(vehicle, many=True).data
        response["driver"] = DriverInformationSerializer(driver, many=True).data

        return Response(response)

    @action(
        methods=["GET"],
        detail=False,
        # permission_classes=[IsAuthenticated, IsCarrier],
        permission_classes=permission_classes,
        url_path="users",
    )
    def users(self, request):
        carrier = self.get_queryset()

        carrier_users = CarrierUser.objects.filter(carrier=carrier)
        print(carrier_users)
        page = self.paginate_queryset(carrier_users)
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            carrier_users,
            many=True,
        )
        response = serializer.data
        return Response(response)

    @action(
        methods=["POST"],
        detail=False,
        # permission_classes=[IsAuthenticated, IsCarrier],
        permission_classes=permission_classes,
        url_path="send-documents",
    )
    def send_documents(self, request):
        carrier = self.get_queryset()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        carrier_documents = serializer.validated_data
        send_documents(
            carrier_id=carrier.id,
            email=carrier_documents.get("email"),
            documents=carrier_documents.get("documents"),
        )
        return Response({"message": "Send Successfully."})
