# from rest_framework.decorators import action
import datetime

from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from nauvus.api.viewsets import BaseModelViewSet
from nauvus.apps.banking.utils import send_payment_to_users
from nauvus.apps.bookings.api.serializers import (
    BookLoadCreateSerializer,
    BookLoadDeliveryDetailsSerializer,
    BookLoadDeliveryProofSerializer,
    BookLoadReassignDriverSerializer,
    BookLoadSerializer,
    BookLoadStopDetailsSerializer,
    ExternalLoadBookingSerializer,
    ExternalLoadInformationSerializer,
    ExternalLoadSerializer,
    ExternalLoadUpdateSerializer,
    FavouriteLoadCreateSerializer,
    FavouriteLoadSerializer,
    LiveShareCreateSerializer,
    LiveShareRetrieveSerializer,
)
from nauvus.apps.bookings.models import (
    BookLoad,
    BookLoadDeliveryProof,
    BookLoadLiveShare,
    ExternalLoad,
    FavouriteLoad,
)
from nauvus.apps.carrier.models import CarrierUser
from nauvus.apps.dispatcher.models import DispatcherUser
from nauvus.apps.driver.models import CarrierDriver, Driver
from nauvus.apps.notifications.models import Notification
from nauvus.auth.api.serializers import UserSerializer
from nauvus.users.models import User

from ....api.permissions import (
    IsCarrier,
    IsCarrierOrDispatcher,
    IsCarrierOrDispatcherOrDriver,
    IsDispatcher,
    IsDriver,
)


class BookLoadViewset(BaseModelViewSet):

    """
    create:
        Book Load.

    update:
        Update Book Load

    retrieve:
        Get Book Load

    destroy:
        Delete Book Load

    list:
        List of Book Load

    delivery_proof:
        Proof of Booked Load Delivery.

    delivery_details:
        Delivery Detatils of Booked Load.

    stop_details:
        Stop Details of Booked Load.
    """

    serializer_class = BookLoadSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    ordering_fields = (
        "id",
        "load__pickup_date",
        "load__amount",
        "status",
        "driver__user__username",
        "dispatcher__organization_name",
    )

    def get_queryset(self):
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        status = self.request.query_params.get("status")
        time = self.request.query_params.get("time")
        if (
            self.request.user.user_type == User.CARRIER_OWNER
            or self.request.user.user_type == User.CARRIER_OWNER_OPERATOR
        ):
            try:
                carrier_user = CarrierUser.objects.get(
                    user=self.request.user, is_current_organization=True
                )
                book_loads = BookLoad.objects.filter(
                    carrier=carrier_user.carrier
                )
            except CarrierUser.DoesNotExist:
                raise NotFound("CarrierUser not found")

        elif self.request.user.user_type == User.DISPATCHER:
            try:
                dispatcher_user = DispatcherUser.objects.get(
                    user=self.request.user, is_current_organization=True
                )
                book_loads = BookLoad.objects.filter(
                    dispatcher=dispatcher_user.dispatcher
                )

            except DispatcherUser.DoesNotExist:
                raise NotFound("DispatcherUser not found")

        elif self.request.user.user_type == User.DRIVER:

            try:
                driver = Driver.objects.get(user=self.request.user)
            except Exception:
                raise NotFound("Driver Not Found.")

            try:
                carrier_driver = CarrierDriver.objects.get(
                    driver=driver, is_current_carrier=True
                )

                book_loads = BookLoad.objects.filter(
                    driver=carrier_driver.driver
                )
            except CarrierDriver.DoesNotExist:
                raise NotFound("CarrierDriver not found")

        else:
            BookLoad.objects.none()

        if start_date and end_date:
            book_loads = book_loads.filter(
                Q(load__pickup_date__gte=start_date)
                & Q(load__pickup_date__lte=end_date)
            )

        elif time:
            current_time = datetime.datetime.now()
            if time == "today":
                book_loads = book_loads.filter(
                    load__pickup_date_time_utc__date=current_time.date()
                )
            elif time == "this year":
                book_loads = book_loads.filter(
                    load__pickup_date_time_utc__year=current_time.year
                )
            elif time == "yesterday":
                book_loads = book_loads.filter(
                    load__pickup_date_time_utc__date=current_time.date()
                    - datetime.timedelta(days=1)
                )
            elif time == "last 7 days":
                book_loads = book_loads.filter(
                    load__pickup_date_time_utc__date__gte=current_time.date()
                    - datetime.timedelta(days=7)
                )
            elif time == "last 30 days":
                book_loads = book_loads.filter(
                    load__pickup_date_time_utc__date__gte=current_time.date()
                    - datetime.timedelta(days=30)
                )
            else:
                pass

        if status:
            if status == BookLoad.IN_PROGRESS:
                book_loads = book_loads.filter(status=status)
            elif status == BookLoad.COMPLETED:
                book_loads = book_loads.filter(status=status)
            elif status == BookLoad.UPCOMING:
                book_loads = book_loads.filter(status=status)
            else:
                pass

        else:
            pass

        # for i in book_loads:
        # a = datetime.datetime.now().strptime("%Y-%m-%d %H:%M:%S")
        # a = datetime.datetime.now().date()
        # print(a, type(a))
        # print(i.load.pickup_date_time_utc)
        # b = datetime.datetime.strptime(
        #     i.load.pickup_date_time_utc, "%a, %d %b %Y %H:%M:%S %Z"
        # ).date()
        #     b = i.load.pickup_date_time_utc.date()
        #     print(b, type(b))
        return book_loads

    def get_serializer_class(self):
        actions = {
            "create": BookLoadCreateSerializer,
            "update": BookLoadReassignDriverSerializer,
            "retrieve": BookLoadSerializer,
            "list": BookLoadSerializer,
            "delivery_proof": BookLoadDeliveryProofSerializer,
            "delivery_details": BookLoadDeliveryDetailsSerializer,
            "stop_details": BookLoadStopDetailsSerializer,
            "live_share": LiveShareCreateSerializer,
            "get_live_share": LiveShareRetrieveSerializer,
        }
        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def get_permissions(self):
        actions = {
            "create": [IsCarrierOrDispatcherOrDriver],
            "list": [IsCarrierOrDispatcherOrDriver],
            "update": [IsCarrierOrDispatcherOrDriver],
            "retrieve": [IsCarrierOrDispatcherOrDriver],
            "delivery_details": [IsCarrierOrDispatcherOrDriver],
            "stop_details": [IsCarrierOrDispatcherOrDriver],
            "live_share": [IsCarrierOrDispatcherOrDriver],
            "delivery_proof": [IsDriver],
            "get_live_share": [AllowAny],
            "live_share": [IsCarrierOrDispatcher],
        }

        if self.action in actions:
            self.permission_classes += actions.get(self.action)

        return super().get_permissions()

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book_load = serializer.save()
        if book_load:
            assign_driver_to_load_notification = (
                Notification.create_assign_driver_to_load_notification(
                    book_load_obj=book_load,
                    carrier_obj=book_load.carrier,
                    dispatcher_obj=book_load.dispatcher,
                    driver_obj=book_load.driver,
                )
            )
            book_load_notification = (
                Notification.create_booked_load_notification(
                    book_load_obj=book_load,
                    carrier_obj=book_load.carrier,
                    dispatcher_obj=book_load.dispatcher,
                    driver_obj=book_load.driver,
                )
            )
        else:
            pass

        return Response(BookLoadSerializer(book_load).data)

    def update(self, request, pk=None):

        try:
            book_load = BookLoad.objects.get(pk=pk)
        except BookLoad.DoesNotExist:
            raise NotFound("BookLoad Not Found.")
        serializer = self.get_serializer(book_load, data=request.data)
        serializer.is_valid(raise_exception=True)
        book_load = serializer.save()

        return Response(BookLoadSerializer(book_load).data)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=permission_classes,
        url_path="delivery-proof",
    )
    def delivery_proof(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        delivery_proof = serializer.save()
        book_load = BookLoad.objects.filter(
            id=delivery_proof.book_load.id
        ).first()
        if book_load:
            book_load.status = BookLoad.COMPLETED
            book_load.save()
            delivery_proof_notification = (
                Notification.create_delivery_proof_notification(
                    book_load_obj=book_load,
                    delivery_proof_obj=delivery_proof,
                    driver_obj=book_load.driver,
                    carrier_obj=book_load.carrier,
                    dispatcher_obj=book_load.dispatcher,
                )
            )
            send_payment = send_payment_to_users(book_load.id)
        else:
            pass

        # if book_load.status == BookLoad.COMPLETED:

        #     if book_load.book_by == BookLoad.CARRIER:

        return Response(BookLoadDeliveryProofSerializer(delivery_proof).data)

    @action(
        methods=["GET"],
        detail=True,
        permission_classes=permission_classes,
        url_path="delivery-details",
    )
    def delivery_details(self, request, pk):
        book_loads = self.get_queryset()
        try:
            book_load = book_loads.get(id=pk)
        except BookLoad.DoesNotExist:
            raise NotFound("BookLoad Not Found")
        return Response(BookLoadDeliveryDetailsSerializer(book_load).data)

    @action(
        methods=["GET"],
        detail=True,
        permission_classes=permission_classes,
        url_path="stop-details",
    )
    def stop_details(self, request, pk):
        book_loads = self.get_queryset()
        try:
            book_load = book_loads.get(id=pk)
        except BookLoad.DoesNotExist:
            raise NotFound("BookLoad Not Found")
        return Response(self.get_serializer(book_load).data)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=permission_classes,
        url_path="get-live-share",
    )
    def get_live_share(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            live_share = BookLoadLiveShare.objects.get(
                uid=serializer.validated_data.get("uid")
            )
        except BookLoadLiveShare.DoesNotExist:
            raise NotFound("BookLoadLiveShare Not Found.")
        current_date = datetime.datetime.now()

        if datetime.datetime.strftime(
            live_share.expiration_date, "%Y-%m-%d %H:%M:%S.%f"
        ) < datetime.datetime.strftime(current_date, "%Y-%m-%d %H:%M:%S.%f"):
            raise NotFound("Sorry The Link is Expired.")

        book_load_delivery_proof = BookLoadDeliveryProof.objects.filter(
            book_load=live_share.book_load
        ).last()

        data = {
            "stop_details": BookLoadStopDetailsSerializer(
                live_share.book_load
            ).data.get("load"),
            "driver": UserSerializer(live_share.book_load.driver.user).data,
            "bill_of_landing": BookLoadDeliveryProofSerializer(
                book_load_delivery_proof
            ).data.get("proof"),
        }

        return Response(data)

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=permission_classes,
        url_path="live-share",
    )
    def live_share(self, request, pk):

        try:
            book_load = BookLoad.objects.get(id=pk)
        except BookLoad.DoesNotExist:
            raise NotFound("BookLoad Not Found")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        live_share = serializer.save()
        live_share.book_load = book_load
        live_share.save()
        data = {"uid": live_share.uid}

        return Response(data)


class FavouriteLoadViewSet(BaseModelViewSet):

    """
    create:
        Create Favourite Load.

    retrieve:
        Get Favourite Load.

    update:
        Update Favourite Load.

    destroy:
        Delete Favourite Load.
    """

    serializer_class = FavouriteLoadSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        try:
            favourite_loads = FavouriteLoad.objects.filter(
                user=self.request.user
            )
            return favourite_loads
        except FavouriteLoad.DoesNotExist:
            raise NotFound("Favourite Load not found")

    def get_serializer_class(self):
        actions = {
            "create": FavouriteLoadCreateSerializer,
            "list": FavouriteLoadSerializer,
        }
        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        favourite_load = serializer.save()

        return Response(FavouriteLoadSerializer(favourite_load).data)


class ExternalLoadBookingViewSet(BaseModelViewSet):

    """
    create:
        Book External Load

    retrieve:
        Get External Load.

    update:
        Update External Load.

    destroy:
        Delete External Load.
    """

    serializer_class = ExternalLoadBookingSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExternalLoad.objects.all()

    def get_serializer_class(self):
        actions = {
            "create": ExternalLoadBookingSerializer,
            "retrieve": ExternalLoadInformationSerializer,
            "update": ExternalLoadUpdateSerializer,
        }
        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        external_loads = serializer.save()
        return Response(ExternalLoadBookingSerializer(external_loads).data)

    def update(self, request, pk=None):
        try:
            external_loads = ExternalLoad.objects.get(pk=pk)
        except ExternalLoad.DoesNotExist:
            raise NotFound("External Load Not Found.")

        serializer = self.get_serializer(external_loads, data=request.data)
        serializer.is_valid(raise_exception=True)
        external_loads = serializer.save()
        return Response(ExternalLoadSerializer(external_loads).data)
