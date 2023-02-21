import random

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from nauvus.api.permissions import DispatcherHasPermission, IsDispatcher
from nauvus.api.viewsets import BaseCreateViewSet, BaseModelViewSet
from nauvus.apps.carrier.api.serializers import (
    CarrierBrokerSerializer,
    CarrierResponseSerializer,
    CurrentCarrierSerializer,
)
from nauvus.apps.carrier.models import Carrier, CarrierBroker, CarrierDispatcher
from nauvus.apps.dispatcher.api.serializers import (
    CurrentDispatcherOrganizationInformationSerializer,
    CurrentDispatcherSerializer,
    DispatcherAdminInvitationCreateSerializer,
    DispatcherAdminInvitationInformationSerializer,
    DispatcherAdminInvitationUserSerializer,
    DispatcherCarrierInformationSerializer,
    DispatcherCarrierUpdateSerializer,
    DispatcherInvitationCreateSerializer,
    DispatcherInvitationInformationSerializer,
    DispatcherInvitationUserSerializer,
    DispatcherOnbordingSerializer,
    DispatcherOrganizationSerializer,
    DispatcherOrganizationUpdateSerializer,
    DispatcherReferenceSerializer,
    DispatcherUserSerializer,
    DispatcherW9InformationSerializer,
)
from nauvus.apps.dispatcher.models import (
    Dispatcher,
    DispatcherInvitation,
    DispatcherUser,
)
from nauvus.auth.api.serializers import (
    EmailUpdateOtpVerfySerializer,
    PasswordOtpGenerateSerializer,
)
from nauvus.auth.tasks import send_invitation_mail, send_password_reset_mail
from nauvus.users.models import EmailUpdateOtpVerification

User = get_user_model()


class DispatcherW9ViewSet(BaseCreateViewSet):

    """
    create:
        Upload w9 Form.

    retrieve:
        Get w9 Form.

    update:
        Update w9 Form.

    destroy:
        Delete w9 Form.
    """

    serializer_class = DispatcherW9InformationSerializer

    permission_classes = [IsAuthenticated, IsDispatcher]

    def create(self, request):

        try:
            dispatcher = DispatcherUser.objects.get(user=request.user)
        except Exception:
            raise NotFound("Dispatcher not found")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dispatcher_w9_form = serializer.save()

        dispatcher_w9_form.dispatcher = dispatcher.dispatcher
        dispatcher_w9_form.save()
        return Response(self.serializer_class(dispatcher_w9_form).data)


class DispatcherReferenceViewset(BaseCreateViewSet):

    """
    create:
        Add Reference

    retrieve:
        Get Reference

    update:
        Update Reference

    destroy:
        Delete Reference

    """

    serializer_class = DispatcherReferenceSerializer
    permission_classes = [IsAuthenticated, IsDispatcher]

    def create(self, request):
        try:
            dispatcher = DispatcherUser.objects.filter(
                user=request.user
            ).first()
        except Exception:
            raise NotFound("Dispatcher not found")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dispatcher_reference = serializer.save()

        dispatcher_reference.dispatcher = dispatcher.dispatcher
        dispatcher_reference.save()
        return Response(self.get_serializer(dispatcher_reference).data)


class DispatcherOganizationInformationViewSet(BaseModelViewSet):

    """
    update:
        Update Email and Phone.

    reset:
        Send Otp For Update email and phone

    list:
        Get Email and Phone
    """

    serializer_class = DispatcherOrganizationSerializer
    permission_classes = [IsAuthenticated, IsDispatcher]

    def get_queryset(self):
        if self.request.user.user_type == User.DISPATCHER:
            dispatcher_users = DispatcherUser.objects.filter(
                user=self.request.user
            ).values_list("dispatcher__id")
            dispachers = Dispatcher.objects.filter(id__in=dispatcher_users)
            if dispachers:
                return dispachers
            else:
                return None
        else:
            raise NotFound("Permission Denied.")

    def get_serializer_class(self):
        actions = {
            "update": DispatcherOrganizationUpdateSerializer,
            "list": DispatcherOrganizationSerializer,
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

        password_reset_key = "".join(random.choices("1234567890", k=4))  # noqa

        user = EmailUpdateOtpVerification(email=email, otp=password_reset_key)
        user.save()

        send_password_reset_mail(user.email, user.otp)
        response = self.get_serializer(user).data
        response["message"] = "Otp has been sent on the mail."
        return Response(response)

    def update(self, request, pk=None):

        serializer = EmailUpdateOtpVerfySerializer(data=request.data)
        serializer.is_valid()

        reset_key = serializer.data.get("otp")
        otp = EmailUpdateOtpVerification.objects.filter(otp=reset_key).first()

        try:
            if otp.otp != reset_key:
                return serializers.ValidationError(
                    {
                        "password_reset_key": "Provided password reset key is invalid."
                    }
                )

        except Exception:
            return None

        try:
            dispatcher = Dispatcher.objects.get(pk=pk)
        except Dispatcher.DoesNotExist:
            raise NotFound("Dispatcher not found")

        serializer = self.get_serializer(dispatcher, data=request.data)
        serializer.is_valid(raise_exception=True)
        dispatcher = serializer.save()

        response = {}
        response["dispatcher"] = DispatcherOrganizationSerializer(
            dispatcher
        ).data
        return Response(response)


class DispatcherOnboardingStatusView(APIView):

    """
    Dispatcher Onboarding Status
    """

    permission_classes = [IsAuthenticated, IsDispatcher]

    def get_object(self):
        dispatcher = DispatcherUser.objects.filter(
            user=self.request.user
        ).first()
        if not dispatcher:
            raise NotFound("Dispatcher not found")
        return dispatcher

    def get(self, request):
        dispatcher = self.get_object()
        return Response(DispatcherOnbordingSerializer(dispatcher).data)


class DispatcherInvitationViewset(BaseModelViewSet):

    """
    create:
        Invite Dispatcher user

    retrieve:
        Get Dispatcher user

    destroy:
        Delete Dispatcher user

    update:
        Update Dispatcher user

    """

    serializer_class = DispatcherInvitationCreateSerializer
    permission_classes = [IsAuthenticated, IsDispatcher]

    def get_queryset(self):
        dispatcher = DispatcherUser.objects.filter(
            user=self.request.user
        ).first()
        dispatcher_user = DispatcherInvitation.objects.filter(
            dispatcher=dispatcher.dispatcher
        )
        return dispatcher_user

    def get_serializer_class(self):
        actions = {
            "list": DispatcherInvitationInformationSerializer,
            "retrieve": DispatcherInvitationUserSerializer,
        }

        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def create(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dispatcher_invitation = serializer.save()
        send_invitation_mail(
            email=request.data.get("email"),
            user=request.data.get("first_name"),
        )
        return Response(self.serializer_class(dispatcher_invitation).data)


class DispatcherAdminInvitationViewset(BaseModelViewSet):

    """
    create:
        Invite Dispatcher Admin

    retrieve:
        Get Dispatcher Admin

    destroy:
        Delete Dispatcher Admin

    update:
        Update Dispatcher Admin
    """

    serializer_class = DispatcherAdminInvitationCreateSerializer
    permission_classes = [IsAuthenticated, IsDispatcher]

    def get_queryset(self):
        dispatcher = DispatcherUser.objects.filter(
            user=self.request.user
        ).first()
        dispatcher_admin = DispatcherUser.objects.filter(
            dispatcher=dispatcher.dispatcher
        )
        return dispatcher_admin

    def get_serializer_class(self):
        actions = {
            "list": DispatcherAdminInvitationInformationSerializer,
            "retrieve": DispatcherAdminInvitationUserSerializer,
        }

        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dispatcher_admin_invitation = serializer.save()
        send_invitation_mail(
            email=request.data.get("email"),
            user=request.data.get("first_name"),
        )
        return Response(
            self.serializer_class(dispatcher_admin_invitation).data
        )


class CurrentDispatcherOrganiztionViewset(BaseModelViewSet):

    """
    update_org:
        Current Dispatcher Organization Information
    """

    serializer_class = CurrentDispatcherOrganizationInformationSerializer
    permission_classes = [IsAuthenticated, IsDispatcher]

    def get_queryset(self):
        try:
            dispatcher_user = DispatcherUser.objects.get(
                user=self.request.user, is_current_organization=True
            )
        except Exception:
            raise NotFound("Current Dispatcher User Not Found.")
        return dispatcher_user.dispatcher

    def get_serializer_class(self):
        actions = {
            "list": CurrentDispatcherSerializer,
            "update_org": CurrentDispatcherOrganizationInformationSerializer,
            "users": DispatcherUserSerializer,
            "admin_users": DispatcherUserSerializer,
        }

        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def get_permissions(self):
        actions = {
            "list": [
                DispatcherHasPermission,
            ],
            "update": [
                DispatcherHasPermission,
            ],
            "users": [
                DispatcherHasPermission,
            ],
            "admin_users": [
                DispatcherHasPermission,
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
        permission_classes=[IsAuthenticated, IsDispatcher],
        url_path="update",
    )
    def update_org(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dispatcher_organization = serializer.data
        dispatcher = DispatcherUser.objects.filter(
            user=request.user, is_current_organization=True
        ).first()
        dispatcher.is_current_organization = False
        dispatcher.save()

        try:
            current_dispatcher_user = DispatcherUser.objects.get(
                user=request.user,
                dispatcher=dispatcher_organization["dispatcher"],
            )
            current_dispatcher_user.is_current_organization = True
            current_dispatcher_user.save()
        except Exception:
            raise ValidationError("Carrier Not Found")

        return Response(
            CurrentDispatcherOrganizationInformationSerializer(
                current_dispatcher_user
            ).data
        )

    @action(
        methods=["GET"],
        detail=False,
        # permission_classes=[IsAuthenticated, IsCarrier],
        permission_classes=permission_classes,
        url_path="users",
    )
    def users(self, request):
        dispatcher = self.get_queryset()

        dispatcher_users = DispatcherUser.objects.filter(
            dispatcher=dispatcher, is_owner=False
        )

        page = self.paginate_queryset(dispatcher_users)
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            dispatcher_users,
            many=True,
        )
        response = serializer.data
        return Response(response)

    @action(
        methods=["GET"],
        detail=False,
        # permission_classes=[IsAuthenticated, IsCarrier],
        permission_classes=permission_classes,
        url_path="admin-users",
    )
    def admin_users(self, request):
        dispatcher = self.get_queryset()

        dispatcher_users = DispatcherUser.objects.filter(
            dispatcher=dispatcher, is_owner=True
        )

        page = self.paginate_queryset(dispatcher_users)
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            dispatcher_users,
            many=True,
        )
        response = serializer.data
        return Response(response)


class DispatcherCarrierviewset(BaseModelViewSet):

    serializer_class = CarrierResponseSerializer
    permission_classes = [IsAuthenticated, IsDispatcher]

    def get_queryset(self):
        if self.request.user.user_type == User.DISPATCHER:
            try:
                dispatcher_user = DispatcherUser.objects.get(
                    user=self.request.user, is_current_organization=True
                )
            except Exception:
                raise NotFound("Dispatcher User Not found.")
            status = self.request.GET.get("status")

            carrier_dispatcher = CarrierDispatcher.objects.filter(
                dispatcher=dispatcher_user.dispatcher
            )
            # ).values_list("carrier__id")
            # carriers = Carrier.objects.filter(id__in=carrier_dispatcher)

            if status:
                if status == "active":
                    carrier_dispatcher = carrier_dispatcher.filter(active=True)
                elif status == "inactive":
                    carrier_dispatcher = carrier_dispatcher.filter(
                        active=False
                    )
                else:
                    pass

            return carrier_dispatcher
        raise NotFound("Permission Denied.")

    def get_serializer_class(self):
        actions = {
            "list": DispatcherCarrierInformationSerializer,
            "retrieve": CurrentCarrierSerializer,
            "update": DispatcherCarrierUpdateSerializer,
            "brokers": CarrierBrokerSerializer,
        }

        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def get_permissions(self):
        actions = {
            "update": [
                DispatcherHasPermission,
            ],
            "delete": [
                DispatcherHasPermission,
            ],
        }

        if self.action in actions:
            self.permission_classes += actions.get(self.action)

        return super().get_permissions()

    def retrieve(self, request, pk):

        try:
            dispatcher_carrier = CarrierDispatcher.objects.get(id=pk)
        except Exception:
            raise NotFound("Carrier Dispatcher NotFound.")

        return Response(self.get_serializer(dispatcher_carrier.carrier).data)

    def update(self, request, pk):

        try:
            dispatcher_carrier = CarrierDispatcher.objects.get(id=pk)
        except Exception:
            raise NotFound("Carrier Dispatcher NotFound.")

        serializer = self.get_serializer(dispatcher_carrier, data=request.data)
        serializer.is_valid(raise_exception=True)
        dispatcher_carrier = serializer.save()

        return Response(
            DispatcherCarrierInformationSerializer(dispatcher_carrier).data
        )

    def get_brokers_by_carriers(self, carrier_id):
        order_by = self.request.GET.get("ordering")

        qs = CarrierBroker.objects.filter(carrier=carrier_id)

        if order_by:
            prefix = ""
            if "-" in order_by:
                prefix = "-"
                order_by = order_by.replace("-", "")

            order_by_qs = {
                "name": "broker__name",
                "username": "username",
                "password": "password",
            }

            qs = qs.order_by(f"{prefix}{order_by_qs.get(order_by, '')}")

        return qs

    @action(
        methods=["GET"],
        detail=True,
        # permission_classes=[IsAuthenticated, IsCarrier],
        permission_classes=permission_classes,
        url_path="brokers",
    )
    def brokers(self, request, pk=None):
        dispatcher_carrier = self.get_object()
        carrier_brokers = self.get_brokers_by_carriers(
            dispatcher_carrier.carrier
        )

        page = self.paginate_queryset(carrier_brokers)
        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            carrier_brokers,
            many=True,
        )
        response = serializer.data
        return Response(response)
