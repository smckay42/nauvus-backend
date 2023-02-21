from django.conf import settings

from nauvus.api.serializers import BaseModelSerializer
from nauvus.apps.carrier.models import CarrierUser

# from nauvus.apps.dispatcher.models import DispatcherUser
from nauvus.apps.invitations.models import Invitation

# from rest_framework.exceptions import NotFound
from nauvus.auth.tasks import send_invitation_mail

app_url = settings.APP_URL


class InvitationCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Invitation
        fields = (
            "invitee_email",
            "invitation_type",
        )

    def validate(self, data):
        # TODO: add any needed validation
        # request = self.context.get("request")
        # user = request.user
        # invitation_type = data.get("invitation_type")
        # email = data.get("invitee_email")

        return data

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        invitationType = validated_data.get("invitation_type")
        inviteeEmail = validated_data.get("invitee_email")

        invitation = Invitation(
            inviter=user,
            invitee_email=inviteeEmail,
            invitation_type=invitationType,
            status=Invitation.PENDING,
        )
        invitation.save()

        # send the email invitation
        send_invitation_mail(
            inviteeEmail, "My org", invitationType, "http://www.nauvus.com", user.first_name, user.last_name
        )

        return invitation


class InvitationSerializer(BaseModelSerializer):
    # inviter_user = UserInformationSerializer()

    class Meta:
        model = Invitation
        exclude = ["updated_at"]

    # override the underlying method to return information about the inviter
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # take the appropriate action based on the invitation type
        if instance.invitation_type == "dispatcher" or instance.invitation_type == "driver":
            carrier_user = CarrierUser.objects.get(user=instance.inviter)
            carrier = carrier_user.carrier
            representation["inviter"] = {
                "first_name": carrier_user.user.first_name,
                "last_name": carrier_user.user.last_name,
                "email": carrier_user.user.email,
                "organization": carrier.organization_name,
            }

        elif instance.invitatation_type == "secondary_user":
            # TODO: determine logic for secondary user
            print("Secondary User Invitation ")

        return representation
