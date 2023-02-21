# import geopy.distance
# from django.db.models import Q
# from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# from nauvus.api.permissions import IsCarrierOrDispatcher, IsDispatcher
from nauvus.api.viewsets import BaseModelViewSet
from nauvus.apps.carrier.models import CarrierDispatcher, CarrierUser
from nauvus.apps.dispatcher.models import DispatcherUser
from nauvus.apps.driver.models import CarrierDriver, Driver

# from nauvus.apps.carrier.models import CarrierUser
# from nauvus.apps.cities.api.serializers import CitySerializer, DistanceSerializer
# from nauvus.apps.cities.models import City
# from nauvus.apps.dispatcher.models import DispatcherUser
from nauvus.apps.invitations.api.serializers import InvitationCreateSerializer, InvitationSerializer
from nauvus.apps.invitations.models import Invitation
from nauvus.users.models import User

# from rest_framework.views import APIView


class InvitationViewset(BaseModelViewSet):
    """
    list:
        Return the list of invitations to/from the user

    create:
        Invite a user to an organization to fill a specific role.

    update:
        Accept or decline the specific. pending invitation.
        Accepts a single parameter of "status" with either "accept" or "decline"

    """

    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):

        invitee = self.request.query_params.get("invitee")
        invitationType = self.request.query_params.get("type")
        if invitee is not None:
            invitee = invitee.lower()

        user_email = self.request.user.email

        if invitee == "true":
            invitations = Invitation.objects.filter(invitee_email=user_email)
        else:
            invitations = Invitation.objects.filter(inviter__in=User.objects.filter(email=user_email))

        # if a type is included, filter the result to be only the type specified
        if invitationType is not None:
            invitations = invitations.filter(invitation_type=invitationType)

        return invitations

    def get_permissions(self):
        actions = {
            "list": [IsAuthenticated],
            "retrieve": [AllowAny],
            "create": [IsAuthenticated],
            "update": [IsAuthenticated],
        }

        if self.action in actions:
            self.permission_classes += actions.get(self.action)

        return super().get_permissions()

    def get_serializer_class(self):
        actions = {
            "create": InvitationCreateSerializer,
            "retrieve": InvitationSerializer,
            "update": InvitationSerializer,
        }

        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invitation = serializer.save()
        return Response(InvitationSerializer(invitation).data)

    def retrieve(self, request, pk):

        try:
            invitation = Invitation.objects.get(uid=pk)
        except Exception:
            raise NotFound("Invitation Not Found.")

        return Response(self.get_serializer(invitation).data)

    def update(self, request, pk):
        # TODO: add validation to ensure that the user is the invitee

        try:
            invitation = Invitation.objects.get(uid=pk, status="pending")

            new_status = request.data.get("status")

            # TODO: update should only happen is the current status is pending.
            if new_status == "accept":
                inviter = invitation.inviter

                # take the appropriate action based on the invitation type

                if invitation.invitation_type == Invitation.DISPATCHER:
                    carrier_user = CarrierUser.objects.get(user=inviter)
                    carrier = carrier_user.carrier
                    dispatcher_user = DispatcherUser.objects.get(
                        user=User.objects.get(email=invitation.invitee_email)
                    )
                    dispatcher = dispatcher_user.dispatcher
                    carrier_dispatcher = CarrierDispatcher(carrier=carrier, dispatcher=dispatcher, active=True)
                    carrier_dispatcher.save()
                elif invitation.invitation_type == Invitation.DRIVER:
                    carrier_user = CarrierUser.objects.get(user=inviter)
                    carrier = carrier_user.carrier
                    driver_user = Driver.objects.get(user=User.objects.get(email=invitation.invitee_email))
                    carrier_driver = CarrierDriver(carrier=carrier, driver=driver_user, active=True)
                    carrier_driver.save()
                elif invitation.invitation_type == Invitation.SECONDARY_USER:
                    print("Secondary User Invitation Accepted")

            elif new_status == "reject":
                print("User rejected the invitation")

            invitation.status = new_status
            invitation.save()
        except Exception:
            raise NotFound("No pending invitation found.")

        # TODO: return a success response
        return Response(self.get_serializer(invitation).data)
