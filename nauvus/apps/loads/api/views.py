import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from nauvus.api.permissions import (
    CarrierHasPermission,
    DispatcherOrDriverOrBookedHasPermission,
    IsAvailable,
    IsCarrierOrDispatcher,
    IsDraft,
    IsPending,
    IsUnderway,
    IsUpcoming,
)
from nauvus.apps.dispatcher.models import DispatcherUser
from nauvus.apps.loads.api.serializers import (
    BookedLoadSerializer,
    CompleteDeliverySerializer,
    CreateLoadSerializer,
    DeleteDeliveryDocumentSerializer,
    DeliveryDocumentSerializer,
    LoadListSerializer,
    LoadSerializer,
    RateConfirmationDocumentSerializer,
)
from nauvus.apps.loads.services import book_load, deliver_load

from ...carrier.models import CarrierUser
from ...driver.models import CarrierDriver
from ..models import DeliveryDocument, Load, LoadSource
from ..utils import update_contact_broker
from .filters import LoadFilter

logger = logging.getLogger(__name__)

User = get_user_model()


class LoadViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Load.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = LoadFilter

    def get_object(self):
        load = get_object_or_404(Load, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, load)
        return load

    def get_queryset(self):
        if self.action == "search":
            return self.queryset.filter(current_status="available")
        return self.queryset

    def get_serializer_class(self):
        if self.action == "deliver":
            return CompleteDeliverySerializer
        if self.action == "delete_document":
            return DeleteDeliveryDocumentSerializer
        if self.action == "book":
            return BookedLoadSerializer
        if self.action == "add_rate_confirmation_document":
            return RateConfirmationDocumentSerializer
        if self.action == "create":
            return CreateLoadSerializer
        if self.action == "list":
            return LoadListSerializer
        if self.action == "retrieve" or self.action == "search":
            return LoadSerializer
        return DeliveryDocumentSerializer

    @permission_classes([IsCarrierOrDispatcher])
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            load = serializer.save(created_by=self.request.user)
        except Exception as e:
            logger.error(f"Invalid data for creating load. {e}")
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"id": str(load.id)}, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["put", "patch"],
        url_path="book",
        permission_classes=[IsCarrierOrDispatcher & (IsAvailable | IsDraft)],
    )
    def book(self, request, validated_data=None, *args, **kwargs):
        load = self.get_object()

        if request.user.user_type == User.DISPATCHER:
            du = DispatcherUser.objects.get(user=request.user)
            load.dispatcher = du

        serializer = self.get_serializer(load, data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            load = serializer.save()
            book_load(load)
        except Exception as e:
            logger.error(f"Invalid data for booking load. {e}")
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"id": str(load.id)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"], url_path="cancel", permission_classes=[IsAuthenticated])
    def cancel(self, request, validated_data=None, *args, **kwargs):
        # load = self.get_object()

        # need to take different actions based on the state of the load and the user
        # for a driver, this should move it back to the carrier/dispatcher

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"], url_path="accept", permission_classes=[IsAuthenticated & IsPending])
    def accept(self, request, validated_data=None, *args, **kwargs):
        load = self.get_object()

        load.current_status = Load.Status.UPCOMING
        load.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"], url_path="start", permission_classes=[IsAuthenticated & IsUpcoming])
    def start(self, request, validated_data=None, *args, **kwargs):
        load = self.get_object()

        load.current_status = Load.Status.UNDERWAY
        load.save()

        return Response(status=status.HTTP_200_OK)

    @action(
        detail=True, methods=["post"], url_path="delivery-documents", permission_classes=[IsAuthenticated & IsUnderway]
    )
    def add_delivery_document(self, request, validated_data=None, *args, **kwargs):
        load = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # save the documents
        serializer.save(load_id=load)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["post"],
        url_path="rate-confirmation",
        permission_classes=[IsAuthenticated & IsAvailable],
    )
    def add_rate_confirmation_document(self, request, validated_data=None, *args, **kwargs):
        load = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # save the document
        load.rc_document = serializer.validated_data.get("document")
        load.save()

        return Response(status=status.HTTP_201_CREATED)

    @add_rate_confirmation_document.mapping.delete
    def delete_rate_confirmation_document(self, request, validated_data=None, *args, **kwargs):
        load = self.get_object()

        # save the document
        load.rc_document = None
        load.save()

        return Response("File deleted", status=status.HTTP_200_OK)

    @add_delivery_document.mapping.get
    def get_delivery_documents(self, request, validated_data=None, *args, **kwargs):

        load = self.get_object()
        docs = DeliveryDocument.objects.filter(load_id=load.id)
        serializer = self.get_serializer(docs, many=True)

        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"], url_path="deliver", permission_classes=[IsAuthenticated & IsUnderway])
    def deliver(self, request, validated_data=None, *args, **kwargs):
        load = self.get_object()

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            deliver_load(load, serializer.validated_data.get("delivered_date"))

        except Exception as e:
            # TODO: improve the exception handling
            raise e

        return Response(status=status.HTTP_200_OK)

    @add_delivery_document.mapping.delete
    def delete_document(self, request, validated_data=None, *args, **kwargs):
        self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doc = DeliveryDocument.objects.get(pk=serializer.validated_data.get("document_id"))
        doc.delete()

        return Response("File deleted", status=status.HTTP_200_OK)

    @permission_classes([IsAuthenticated])
    def list(self, request, *args, **kwargs) -> Response:
        """Return the loads for the current user"""

        current_user = self.request.user
        logger.debug(f"Retrieving loads for {current_user}")
        carrier = CarrierUser.get_current_organization(current_user)
        carrier_drivers = CarrierDriver.objects.filter(carrier=carrier).values("driver")

        queryset = self.queryset.filter(
            Q(created_by=current_user)
            | Q(dispatcher__user=current_user)
            | Q(driver__user=current_user)
            | Q(driver__in=carrier_drivers)
        ).order_by("-updated_at")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="search", permission_classes=[IsAuthenticated])
    def search(self, request, validated_data=None, *args, **kwargs):
        """Search available loads"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @permission_classes([IsAvailable | CarrierHasPermission | DispatcherOrDriverOrBookedHasPermission])
    def retrieve(self, request, *args, **kwargs):
        """Retrieve the details about a load."""
        instance = self.get_object()

        # TODO: move to service layer
        if isinstance(instance.source, LoadSource):
            load_id = instance.id
            broker_id = instance.broker.id
            external_load_id = instance.source.load_id

            source_name = instance.source.source

            try:
                # Update the load contact and broker
                update_contact_broker(source_name, load_id, broker_id, external_load_id)
            except ObjectDoesNotExist:
                message = {"message": f"Load no longer present at source {source_name}"}
                return Response(
                    message,
                    status=status.HTTP_404_NOT_FOUND,
                )

            instance = self.get_object()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
