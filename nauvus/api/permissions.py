# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import BasePermission, IsAdminUser

from nauvus.apps.carrier.models import CarrierUser
from nauvus.apps.dispatcher.models import DispatcherUser
from nauvus.apps.driver.models import CarrierDriver
from nauvus.apps.loads.models import Load
from nauvus.users.models import User


class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active and request.user.is_superuser)


# class IsAuthenticated(BasePermission):
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_active)


class IsNauvusAdministratorOrNauvusBackroomStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_active
            and (
                request.user.user_type == User.NAUVUS_ADMINISTRATOR
                or request.user.user_type == User.NAUVUS_BACKROOM_STAFF
            )
        )


class IsCarrier(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_active
            and (request.user.user_type == User.CARRIER_OWNER or request.user.user_type == User.CARRIER_OWNER_OPERATOR)
        )


class IsDispatcher(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active and request.user.user_type == User.DISPATCHER)


class IsDriver(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active and request.user.user_type == User.DRIVER)


class IsCarrierOrDispatcher(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_active
            and (
                request.user.user_type == User.CARRIER_OWNER
                or request.user.user_type == User.CARRIER_OWNER_OPERATOR
                or request.user.user_type == User.DISPATCHER
            )
        )


class IsCarrierOrDispatcherOrDriver(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_active
            and (
                request.user.user_type == User.CARRIER_OWNER
                or request.user.user_type == User.CARRIER_OWNER_OPERATOR
                or request.user.user_type == User.DISPATCHER
                or request.user.user_type == User.DRIVER
            )
        )


class CarrierHasPermission(BasePermission):
    def has_permission(self, request, view):
        if (
            request.user
            and request.user.is_active
            and (request.user.user_type == User.CARRIER_OWNER or request.user.user_type == User.CARRIER_OWNER_OPERATOR)
        ):
            carrier_user = CarrierUser.objects.filter(user=request.user, access_type=CarrierUser.FULL_ADMIN)
            if carrier_user:
                return True
            return False
        return False


class DispatcherHasPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_active and request.user.user_type == User.DISPATCHER:
            dispatcher_user = DispatcherUser.objects.filter(user=request.user, access_type=DispatcherUser.FULL_ADMIN)
            if dispatcher_user:
                return True
            return False
        return False


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        dispatcher_owner = DispatcherUser.objects.filter(
            user=request.user, is_owner=True, user__user_type=User.DISPATCHER
        ).first()
        return bool(
            request.user
            and request.user.is_active
            and (
                request.user.user_type == User.CARRIER_OWNER
                or request.user.user_type == User.DRIVER
                or dispatcher_owner
            )
        )


class IsNauvusBackRoomStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_active
            and (
                request.user.user_type == User.NAUVUS_BACKROOM_STAFF
                or request.user.user_type == User.NAUVUS_ADMINISTRATOR
            )
        )


class DispatcherOrDriverOrBookedHasPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if obj.current_status == "available":
            return (
                request.user.user_type == User.CARRIER_OWNER
                or request.user.user_type == User.CARRIER_OWNER_OPERATOR
                or request.user.user_type == User.DISPATCHER
            )
        if obj.dispatcher and obj.driver:
            return request.user == obj.dispatcher.user or request.user == obj.driver.user
        elif obj.dispatcher and not obj.driver:
            return request.user == obj.dispatcher.user
        elif obj.driver and not obj.dispatcher:
            return request.user == obj.driver.user
        else:
            return False


class IsLoadCarrier(BasePermission):
    """Returns true is the user is the carrier of the load"""

    def __is_load_carrier(self, request, obj):
        """Helper function to determine if the user is the carrier of the load"""
        user = request.user
        load = obj
        carrier_user = CarrierUser.get_by_user(user)

        carrier_drivers = CarrierDriver.objects.filter(carrier=carrier_user.carrier)

        # if the load driver is in the list of drivers for the carrier, then return true
        try:
            carrier_drivers.get(driver=load.driver)

        except ObjectDoesNotExist:
            return False

        return True

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_active
            and (request.user.user_type == User.CARRIER_OWNER or request.user.user_type == User.CARRIER_OWNER_OPERATOR)
        )

    def has_object_permission(self, request, view, obj):
        return self.__is_load_carrier(request, obj)


class IsDelivered(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.current_status == Load.Status.DELIVERED


class IsBooked(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.current_status == Load.Status.BOOKED


class IsPending(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.current_status == Load.Status.PENDING


class IsUpcoming(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.current_status == Load.Status.UPCOMING


class IsUnderway(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.current_status == Load.Status.UNDERWAY


class IsAvailable(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.current_status == Load.Status.AVAILABLE


class IsDraft(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.current_status == Load.Status.DRAFT
