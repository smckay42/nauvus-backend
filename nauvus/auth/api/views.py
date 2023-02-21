# import the logging library
import logging
import random
import string

# from dj_rest_auth.serializers import JWTSerializer
from dj_rest_auth.views import LoginView
from django.conf import settings
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from nauvus.api.permissions import IsNauvusBackRoomStaff
from nauvus.api.viewsets import BaseCreateViewSet, BaseModelViewSet
from nauvus.apps.carrier.models import Carrier, CarrierUser
from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.auth.api.serializers import (
    CarrierSignUpSerializer,
    DispatcherSignUpSerializer,
    DriverLoginSerializer,
    DriverSignUpSerializer,
    JWTSerializer,
    LoginCarrierResponseSerializer,
    LoginDispatcherResponseSerializer,
    LoginResponseSerializer,
    NauvusBackRoomStaffLoginSerializer,
    NauvusBackroomStaffSignUpSerializer,
    PasswordOtpGenerateSerializer,
    PasswordOtpVerifySerializer,
    SignUpOtpGenerateSerializer,
    SignUpOtpVerifySerializer,
    UserInformationSerializer,
    UserSerializer,
)
from nauvus.auth.tasks import send_nauvus_service_agreement, send_password_reset_mail, send_welcome_mail
from nauvus.auth.utils import create_user_account_stripe
from nauvus.services import twilio
from nauvus.services.credit.oatfi.api import Oatfi
from nauvus.users.models import User

# Get an instance of a logger
logger = logging.getLogger(__name__)


class InitiateSignUpViewset(BaseCreateViewSet):

    serializer_class = SignUpOtpGenerateSerializer

    permission_classes = [
        AllowAny,
    ]

    def create(self, request):
        """
        Validate phone number and send otp for signup process.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_verification = serializer.save()

        # enable override in lower environments
        otp_override = settings.OTP_CODE_OVERRIDE

        # if override is present, never call twilio
        if otp_override is not None:
            return Response(self.get_serializer(otp_verification).data)

        try:
            twilio_client = twilio.TwilioClient()
            otp_response = twilio_client.send_sms(
                otp_verification.phone,
                f"Your Nauvus signup verification code is:{otp_verification.otp}",
            )
            if not otp_response:
                return Response({"error": "Error in sending OTP."})
        except Exception as e:
            logger.error(e)
            return Response({"error": "Error in sending OTP."})

        return Response(self.get_serializer(otp_verification).data)


class VerifySignUpOTPViewset(BaseCreateViewSet):

    serializer_class = SignUpOtpVerifySerializer

    permission_classes = [
        AllowAny,
    ]

    def create(self, request):
        """
        Verify otp for signup process.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_verification = serializer.save()
        return Response(SignUpOtpGenerateSerializer(otp_verification).data)


class PasswordResetViewset(BaseCreateViewSet):

    permission_classes = [
        AllowAny,
    ]

    def get_serializer_class(self):
        actions = {
            "reset": PasswordOtpGenerateSerializer,
            "verification": PasswordOtpVerifySerializer,
        }
        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[AllowAny],
        url_path="change",
    )
    def create_new_password(self, request, *args, **kwargs):
        """
        Reset Password.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = {"msg": "Password change sucessfully."}
        return Response(response)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[AllowAny],
        url_path="reset",
    )
    def reset(self, request):
        """
        Validate email and send otp for password reset.  If email is not found in the system, do nothing.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        user_email = serializer.data["email"]

        response = request.data
        response["message"] = "Password reset email sent if user is in the system."

        try:
            user = User.objects.get(email=user_email.lower())
            reset_key = "".join(random.choices(string.ascii_lowercase + string.digits, k=14))
            user.password_reset_key = reset_key  # noqa
            user.save()
            send_password_reset_mail(user.email, user.password_reset_key)
        except Exception:
            logger.error(f"Password reset requested for {user_email} but user not found.")

        return Response(response)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[AllowAny],
        url_path="reset/confirm",
    )
    def verification(self, request):
        """
        Validate email and send otp for password reset process.
        """

        serializer = PasswordOtpVerifySerializer(data=request.data)
        serializer.is_valid()

        password_reset_key = serializer.data.get("password_reset_key")

        try:
            user = User.objects.get(
                password_reset_key=password_reset_key,
            )
        except Exception:
            raise serializers.ValidationError({"password_reset_key": "Provided password reset key is invalid."})

        user.set_password(serializer.data["password"])
        user.password_reset_key = None
        user.save()
        response = PasswordOtpGenerateSerializer(user).data
        response["message"] = "Password updated succssfully."
        return Response(response)


class RegistrationViewset(BaseCreateViewSet):

    """
    carrier: Carrier Registration Procress.
    dispatcher: Dispatcher Registration Procress.
    """

    serializer_class = CarrierSignUpSerializer

    permission_classes = [
        AllowAny,
    ]

    def get_serializer_class(self):
        actions = {
            "carrier": CarrierSignUpSerializer,
            "dispatcher": DispatcherSignUpSerializer,
            "nauvus_backroom_staff": NauvusBackroomStaffSignUpSerializer,
            "driver": DriverSignUpSerializer,  # TODO
        }

        if self.action in actions:
            self.serializer_class = actions.get(self.action)

        return super().get_serializer_class()

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[AllowAny],
        url_path="carrier",
    )
    def carrier(self, request, *args, **kwargs):
        """
        Carrier Registration Procress.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        email = request.data.get("email")
        stripe_customer_id = create_user_account_stripe(email)
        user.stripe_customer_id = stripe_customer_id
        user.save()

        # TODO: this appears to be the same code for dispatcher and carrier - should this be a single call?
        # jwt token
        # access_token, refresh_token = jwt_encode(user)
        refresh = RefreshToken.for_user(user)
        # send_welcome_mail(
        #     email=request.data.get("email"),
        #     user=request.data.get("first_name"),
        # )

        user_data = UserSerializer(user).data

        send_nauvus_service_agreement.delay(user.id)
        send_welcome_mail.delay(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        carrier_user = CarrierUser.get_by_user(user)
        # send the carrier to oatfi once they have a stripe account
        Oatfi().save_carrier(carrier_user)
        carrier = Carrier.objects.get(id=carrier_user.carrier.id)
        organization = LoginCarrierResponseSerializer(carrier).data

        response = {}
        response["user"] = user_data
        response["access_token"] = str(refresh.access_token)
        response["refresh_token"] = str(refresh)
        response["carrier"] = organization
        return Response(response)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[AllowAny],
        url_path="dispatcher",
    )
    def dispatcher(self, request, *args, **kwargs):
        """
        Dispatcher Registration Procress.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # jwt token
        # access_token, refresh_token = jwt_encode(user)
        refresh = RefreshToken.for_user(user)
        # send_welcome_mail(
        #     email=request.data.get("email"),
        #     user=request.data.get("first_name"),
        # )

        user_data = UserSerializer(user).data

        send_nauvus_service_agreement.delay(user.id)
        send_welcome_mail.delay(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        dispatcher_user = DispatcherUser.get_by_user(user)
        dispatcher = Dispatcher.objects.get(id=dispatcher_user.dispatcher.id)
        organization = LoginDispatcherResponseSerializer(dispatcher).data

        response = {}
        response["user"] = user_data
        response["access_token"] = str(refresh.access_token)
        response["refresh_token"] = str(refresh)
        response["dispatcher"] = organization
        return Response(response)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[AllowAny],
        url_path="driver",
    )
    def driver(self, request, *args, **kwargs):
        """
        Driver Registration Procress.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        driver = serializer.save()

        refresh = RefreshToken.for_user(driver.user)

        # jwt token
        user_data = UserSerializer(driver.user).data

        send_nauvus_service_agreement.delay(driver.user.id)
        send_welcome_mail.delay(
            email=driver.user.email,
            first_name=driver.user.first_name,
            last_name=driver.user.last_name,
        )

        response = {}
        response["user"] = user_data
        response["access_token"] = str(refresh.access_token)
        response["refresh_token"] = str(refresh)

        return Response(response)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[IsAuthenticated, IsNauvusBackRoomStaff],
        url_path="nauvus-backroom-staff",
    )
    def nauvus_backroom_staff(self, request, *args, **kwargs):
        """
        Nauvus Backroom Staff Registration Procress.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # refresh = RefreshToken.for_user(user)

        # jwt token
        user_data = UserSerializer(user).data
        # send_nauvus_service_agreement(user.id)
        # carrier_user = CarrierUser.get_by_user(user)
        # carrier = Carrier.objects.get(id=carrier_user.carrier.id)
        # organization = LoginCarrierResponseSerializer(carrier).data

        response = {}
        response["user"] = user_data
        # response["access_token"] = str(refresh.access_token)
        # response["refresh_token"] = str(refresh)
        # response["carrier"] = organization
        return Response(response)


class UserInformationViewset(BaseModelViewSet):

    serializer_class = LoginResponseSerializer

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        actions = {
            "list": UserInformationSerializer,
        }

        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def list(self, request):

        user = User.objects.get(id=request.user.id)

        return Response(data=self.get_serializer(user).data)


class DriverLoginView(LoginView):

    serializer_class = DriverLoginSerializer

    def get_response_serializer(self):
        return JWTSerializer


class NauvusBackRoomStaffLoginView(LoginView):

    serializer_class = NauvusBackRoomStaffLoginSerializer

    def get_response_serializer(self):
        return JWTSerializer
