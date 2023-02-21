import logging
import random

from dj_rest_auth.serializers import LoginSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers

from nauvus.api.serializers import BaseModelSerializer
from nauvus.apps.carrier.models import Carrier, CarrierTrailerSize, CarrierTrailerType, CarrierUser
from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.apps.driver.models import CarrierDriver, Driver

# from nauvus.services.stripe import StripeClient
from nauvus.users.models import Address, EmailUpdateOtpVerification, SignUpOtpVerification

User = get_user_model()


# helper method to get the organization information for a user
def get_user_organization(user):
    try:
        if user.user_type == user.CARRIER_OWNER or user.user_type == User.CARRIER_OWNER_OPERATOR:
            carrier_user = CarrierUser.objects.get(user=user, is_owner=True)
            organization_data = LoginCarrierResponseSerializer(carrier_user.carrier).data
        elif user.user_type == user.DISPATCHER:
            dispatcher_user = DispatcherUser.objects.filter(user=user, is_owner=True).first()
            if dispatcher_user:
                organization_data = LoginDispatcherResponseSerializer(dispatcher_user.dispatcher).data
            else:
                organization_data = {}
        elif user.user_type == User.DRIVER:
            driver = Driver.objects.get(user=user)
            carrier_driver = CarrierDriver.objects.get(driver=driver, is_current_carrier=True)
            organization_data = LoginCarrierResponseSerializer(carrier_driver.carrier).data
        else:
            organization_data = {}

        return organization_data
    except Exception:
        logging.error(Exception)
        return None


class SignUpOtpGenerateSerializer(BaseModelSerializer):

    """Signup Otp Generate"""

    class Meta:
        model = SignUpOtpVerification
        fields = (
            "phone",
            "signup_process_id",
        )
        read_only_fields = ("signup_process_id",)

    def validate_phone(self, value):
        users = User.objects.filter(phone=value)
        if users:
            raise serializers.ValidationError("User is already exist with the given phone number.")

        return value

    def create(self, validated_data):
        otp_verification, _ = SignUpOtpVerification.objects.get_or_create(phone=validated_data["phone"])

        # enable override in lower environments
        otp_override = settings.OTP_CODE_OVERRIDE

        if otp_override is None:
            otp_verification.otp = "".join(random.choices("1234567890", k=4))  # noqa
        else:
            otp_verification.otp = otp_override
        otp_verification.verified = False
        otp_verification.save()
        return otp_verification


class SignUpOtpVerifySerializer(BaseModelSerializer):

    """
    Verify SignupOtp
    """

    class Meta:
        model = SignUpOtpVerification
        fields = ("phone", "otp", "signup_process_id")
        read_only_fields = ("signup_process_id",)

    def validate(self, data):
        otp = data.get("otp")
        phone = data.get("phone")
        signup_verification = SignUpOtpVerification.objects.filter(phone=phone, otp=otp).first()
        if not signup_verification:
            raise serializers.ValidationError("Provided OTP is invalid.")
        return data

    def create(self, validated_data):
        otp_verification = SignUpOtpVerification.objects.filter(
            phone=validated_data["phone"], otp=validated_data["otp"]
        ).first()
        otp_verification.verified = True
        otp_verification.save()
        return otp_verification


class PasswordOtpGenerateSerializer(BaseModelSerializer):

    """Reset Password Otp"""

    class Meta:
        model = User
        fields = ["email"]


class PasswordOtpVerifySerializer(BaseModelSerializer):

    """Verify Reset Password Otp"""

    class Meta:
        model = User
        fields = ["password_reset_key", "password"]


class EmailUpdateOtpVerfySerializer(BaseModelSerializer):

    """Otp For Update the Email"""

    class Meta:
        model = EmailUpdateOtpVerification
        fields = ("email", "otp")


class CarrierSerializer(BaseModelSerializer):

    """Carrier's Information"""

    class Meta:
        model = Carrier
        fields = (
            "id",
            "organization_name",
            "mc_number",
            "dot_number",
        )


class AddressSerializer(BaseModelSerializer):

    """Addess Information Serializer"""

    class Meta:
        model = Address

        fields = [
            "id",
            "street1",
            "street2",
            "city",
            "state",
            "zip_code",
            "permenent_address",
        ]


class NauvusBackroomStaffSignUpSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password", "phone")

    def create(self, validated_data):
        # create user
        user = User(
            email=validated_data.get("email"),
            user_type=User.NAUVUS_BACKROOM_STAFF,
            phone=validated_data.get("phone"),
        )
        user.set_password(validated_data["password"])
        user.save()

        return user


class DriverSignUpSerializer(BaseModelSerializer):

    signup_process_id = serializers.UUIDField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = Driver
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "signup_process_id",
        )

    def validate_signup_process_id(self, value):
        signup_verification = SignUpOtpVerification.objects.filter(signup_process_id=value).first()
        if not signup_verification:
            raise serializers.ValidationError("Provided signup_process_id is invalid.")

        if not signup_verification.verified:
            raise serializers.ValidationError("Phone number is not verified.")

        return signup_verification

    def create(self, validated_data):
        signup_verification = validated_data.get("signup_process_id")

        # create user
        user = User(
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            email=validated_data.get("email"),
            # set username to be the email address for now
            username=validated_data.get("email"),
            user_type=User.DRIVER,
            phone=signup_verification.phone,
        )
        user.set_password(validated_data["password"])
        user.save()
        signup_verification.delete()

        # Crate Driver
        driver = Driver(
            user=user,
            # available=validated_data.get("available", True),
        )
        driver.save()

        return driver


class CarrierSignUpSerializer(BaseModelSerializer):

    """Carrier Signup Serializer"""

    address = AddressSerializer()
    carrier = CarrierSerializer()
    signup_process_id = serializers.UUIDField()
    # last_name = serializers.CharField(max_length=300, required=True)
    trailer_size = serializers.ListField(child=serializers.CharField())
    trailer_type = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "address",
            "carrier",
            "trailer_size",
            "trailer_type",
            "signup_process_id",
        )

    def validate_signup_process_id(self, value):
        signup_verification = SignUpOtpVerification.objects.filter(signup_process_id=value).first()
        if not signup_verification:
            raise serializers.ValidationError("Provided signup_process_id is invalid.")

        if not signup_verification.verified:
            raise serializers.ValidationError("Phone number is not verified.")

        return signup_verification

    def create(self, validated_data):
        signup_verification = validated_data.get("signup_process_id")

        # create user
        user = User(
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            email=validated_data.get("email"),
            user_type=User.CARRIER_OWNER,
            phone=signup_verification.phone,
        )
        user.set_password(validated_data["password"])
        user.save()
        signup_verification.delete()

        # create address
        address_data = validated_data.get("address")
        state_abbreviation = Address.get_state_abbreviation(address_data.get("state"))
        address = Address(
            user=user,
            street1=address_data.get("street1"),
            street2=address_data.get("street2"),
            city=address_data.get("city"),
            state=state_abbreviation,
            zip_code=address_data.get("zip_code"),
            permenent_address=address_data.get("permenent_address", True),
        )
        address.save()

        # create carrier
        # for now, save the same address for the user and the carrier
        carrier_data = validated_data.get("carrier")
        carrier = Carrier(
            no_of_trucks=carrier_data.get("no_of_trucks"),
            no_of_trailers=carrier_data.get("no_of_trailers"),
            factoring_company_name=carrier_data.get("factoring_company_name"),
            gross_weekly_revenue=carrier_data.get("gross_weekly_revenue"),
            organization_name=carrier_data.get("organization_name"),
            source=carrier_data.get("source"),
            mc_number=carrier_data.get("mc_number"),
            dot_number=carrier_data.get("dot_number"),
            street1=address_data.get("street1"),
            street2=address_data.get("street2"),
            city=address_data.get("city"),
            state=state_abbreviation,
            zip_code=address_data.get("zip_code"),
        )
        carrier.save()

        # create carrier user
        carrier_user = CarrierUser(
            user=user,
            carrier=carrier,
            access_type=CarrierUser.FULL_ADMIN,
            is_current_organization=True,
            is_owner=True,
        )
        carrier_user.save()

        # create account in stripe
        # account = StripeClient.create_account(
        #     type="custom",
        #     country="US",
        #     capabilities={
        #         "card_payments": {"requested": True},
        #         "transfers": {"requested": True},
        #     },
        #     tos_acceptance={"date": 1609798905, "ip": "8.8.8.8"},
        #     business_type="company",
        #     settings={"payments": {"statement_descriptor": "NAUVUS"}},
        #     business_profile={
        #         "name": "test",
        #         "url": "demo.com",
        #         "mcc": "5734",
        #     },
        #     company={
        #         "address": {
        #             "city": "Pomona",
        #             "country": "US",
        #             "line1": "248 W 2nd St",
        #             "line2": "null",
        #             "postal_code": "91766",
        #             "state": "CA",
        #         },
        #         "name": "Travis logistics",
        #         "phone": "+12345678895",
        #         "structure": "multi_member_llc",
        #         "tax_id": "12-3456789",
        #         "directors_provided": "true",
        #         "executives_provided": "true",
        #         "owners_provided": "true",
        #     },
        #     email="davidpeterson@yopmail.com",
        #     external_account={
        #         "object": "bank_account",
        #         "country": "US",
        #         "currency": "usd",
        #         "account_holder_name": "test user",
        #         "account_holder_type": "individual",
        #         "account_number": "000123456789",
        #         "routing_number": "110000000",
        #     },
        # )

        # if account and account.get("id", None):
        #     user.stripe_customer_id = account.get("id")
        #     user.save()

        # StripeClient.create_person(
        #     id=account.get("id"),
        #     id_number="122-33-4626",
        #     first_name="leo",
        #     last_name="bryan",
        #     email="leo@yopmail.com",
        #     relationship={
        #         "title": "ceo",
        #         "percent_ownership": 25,
        #         "representative": "true",
        #         "owner": "true",
        #     },
        #     dob={"day": 12, "month": 12, "year": 2000},
        #     address={
        #         "city": "Pomona",
        #         "country": "US",
        #         "line1": "248 W 2nd St",
        #         "line2": "null",
        #         "postal_code": "91766",
        #         "state": "CA",
        #     },
        #     ssn_last_4=8888,
        #     phone="(201) 211-6846",
        # )

        # create trailer type and size
        trailer_sizes = validated_data.get("trailer_size")
        trailer_types = validated_data.get("trailer_type")

        for trailer_size in trailer_sizes:
            CarrierTrailerSize.objects.create(carrier=carrier, trailer_size=trailer_size)

        for trailer_type in trailer_types:
            CarrierTrailerType.objects.create(carrier=carrier, trailer_type=trailer_type)
        return carrier_user.user


class UserSerializer(BaseModelSerializer):

    """User Response Serializer"""

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "user_type",
        )


class UserInformationSerializer(BaseModelSerializer):

    """Login User Information Serializer"""

    organization = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "user_type",
            "organization",
        )

    def get_organization(self, obj):
        return get_user_organization(obj)

    def to_representation(self, obj):
        # get the original representation
        ret = super(UserInformationSerializer, self).to_representation(obj)
        # request = self.context.get("request")
        # remove 'url' field if mobile request
        if obj.user_type == User.NAUVUS_BACKROOM_STAFF or obj.user_type == User.NAUVUS_ADMINISTRATOR:
            ret.pop("organization")

        # return the modified representation
        return ret


class DispatcherSerializer(BaseModelSerializer):

    """Dispatcher Information Serializer"""

    class Meta:
        model = Dispatcher
        fields = (
            "source",
            "amount_of_experience",
            # "driver_type",
            # "driver_or_carrier_to_onboard",
            "organization_name",
            "number_of_dispatcher",
            "no_of_drivers",
        )


class DispatcherSignUpSerializer(BaseModelSerializer):

    """Dispatcher Signup Serializer"""

    address = AddressSerializer()
    dispatcher = DispatcherSerializer()
    signup_process_id = serializers.UUIDField()

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "address",
            "dispatcher",
            "signup_process_id",
        )

    def validate_signup_process_id(self, value):
        signup_verification = SignUpOtpVerification.objects.filter(signup_process_id=value).first()
        if not signup_verification:
            raise serializers.ValidationError("Provided signup_process_id is invalid.")

        if not signup_verification.verified:
            raise serializers.ValidationError("Phone number is not verified.")

        return signup_verification

    def create(self, validated_data):
        signup_verification = validated_data.get("signup_process_id")

        # create user
        user = User(
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            email=validated_data.get("email"),
            user_type=User.DISPATCHER,
            phone=signup_verification.phone,
        )
        user.set_password(validated_data["password"])
        user.save()
        signup_verification.delete()

        # create address
        address_data = validated_data.get("address")
        address = Address(
            user=user,
            street1=address_data.get("street1"),
            street2=address_data.get("street2"),
            city=address_data.get("city"),
            state=address_data.get("state"),
            zip_code=address_data.get("zip_code"),
            permenent_address=address_data.get("permenent_address", True),
        )
        address.save()

        # create dispatcher
        dispatcher_data = validated_data.get("dispatcher")
        dispatcher = Dispatcher(
            source=dispatcher_data.get("source"),
            amount_of_experience=dispatcher_data.get("amount_of_experience"),
            # driver_type=dispatcher_data.get("driver_type"),
            # driver_or_carrier_to_onboard=dispatcher_data.get(
            #     "driver_or_carrier_to_onboard"
            # ),
            organization_name=dispatcher_data.get("organization_name"),
            number_of_dispatcher=dispatcher_data.get("number_of_dispatcher"),
            no_of_drivers=dispatcher_data.get("no_of_drivers"),
        )
        dispatcher.save()

        # create dispatcher user
        dispatcher_user = DispatcherUser(
            user=user,
            dispatcher=dispatcher,
            access_type=DispatcherUser.FULL_ADMIN,
            is_current_organization=True,
            is_owner=True,
        )
        dispatcher_user.save()

        # Removing support for stripe for now.  This will be added back as part of onboarding.
        # account = StripeClient.create_account(
        #     type="custom",
        #     country="US",
        #     # email=user.email,
        #     capabilities={
        #         "card_payments": {"requested": True},
        #         "transfers": {"requested": True},
        #     },
        # )

        # if account and account.get("id", None):
        #     user.stripe_customer_id = account.get("id")
        #     user.save()

        return dispatcher_user.user


class LoginResponseSerializer(BaseModelSerializer):

    """Dispaly User detail in Login Response."""

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "user_type",
        )


class LoginCarrierResponseSerializer(BaseModelSerializer):

    """Display Carrier detail in Login Response."""

    class Meta:
        model = Carrier
        fields = ("organization_name", "mc_number", "dot_number", "fleet_id")


class LoginDispatcherResponseSerializer(BaseModelSerializer):

    """Display Dispatcher detail in Login Reponse."""

    class Meta:
        model = Dispatcher
        # exclude = ("driver_or_carrier_to_onboard",)
        fields = ["organization_name"]


class JWTSerializer(serializers.Serializer):
    """
    Override dj-rest-auth JWTSerializer for update login response.
    """

    user = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()

    def get_user(self, obj):
        user = obj["user"]
        user_data = LoginResponseSerializer(user).data
        return user_data

    def get_organization(self, obj):
        return get_user_organization(obj["user"])

    def to_representation(self, obj):
        # get the original representation
        ret = super(JWTSerializer, self).to_representation(obj)
        user = obj["user"]
        # remove 'url' field if mobile request
        if user.user_type == User.NAUVUS_BACKROOM_STAFF or user.user_type == User.NAUVUS_ADMINISTRATOR:
            ret.pop("organization")

        # return the modified representation
        return ret


class DriverLoginSerializer(LoginSerializer):

    """Override dj-rest-auth For Driver Login."""

    def _validate_username(self, username, password):
        if username and password:
            driver_user = User.objects.filter(
                username=username,
                user_type=(User.DRIVER),
            )
            if driver_user:
                user = self.authenticate(username=username, password=password)
            else:
                msg = _("Permission Not Allowed..")
                raise exceptions.ValidationError(msg)

        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def get_auth_user_using_allauth(self, username, email, password):
        return self._validate_username(username, password)


class NauvusBackRoomStaffLoginSerializer(LoginSerializer):

    """Override dj-rest-auth For Nauvus Backroom Staff Login."""

    def _validate_email(self, email, password):

        if email and password:
            nauvus_user = User.objects.filter(
                email=email,
                user_type=(User.NAUVUS_BACKROOM_STAFF or User.NAUVUS_ADMINISTRATOR),
            )
            if nauvus_user:
                user = self.authenticate(email=email, password=password)
            else:
                msg = _("Permission Not Allowed..")
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user
