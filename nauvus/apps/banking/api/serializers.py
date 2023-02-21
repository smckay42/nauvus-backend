from rest_framework import serializers

from nauvus.api.serializers import BaseSerializer


class StripeCreateAccountLinkSerializer(serializers.Serializer):
    refresh_url = serializers.URLField()
    return_url = serializers.URLField()


class BankAccountCreateSerializer(BaseSerializer):
    object = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=10)
    currency = serializers.CharField(max_length=10)
    account_holder_name = serializers.CharField(max_length=100)
    account_holder_type = serializers.CharField(max_length=100)
    account_number = serializers.CharField(max_length=100)
    routing_number = serializers.CharField(max_length=100)


class StripeConnectCreateSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=50, required=False, default="custom")
    country = serializers.CharField(max_length=50, required=False, default="US")
    business_type = serializers.CharField(max_length=50, required=False, default="individual")
    business_profile_name = serializers.CharField(max_length=100, required=True)
    business_profile_mcc = serializers.CharField(max_length=100, required=True)
    currency = serializers.CharField(max_length=50, required=False, default="usd")

    account_number = serializers.CharField(max_length=20, required=True)
    routing_number = serializers.CharField(max_length=50, required=False)
    id_number = serializers.CharField(max_length=50, required=True)
    person_email = serializers.CharField(max_length=50, required=True)
    day = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True)
    year = serializers.IntegerField(required=True)
    person_address_line1 = serializers.CharField(max_length=50, required=True)
    person_address_line2 = serializers.CharField(max_length=50, required=False)
    person_address_city = serializers.CharField(max_length=50, required=True)
    person_address_state = serializers.CharField(max_length=50, required=True)
    person_address_country = serializers.CharField(max_length=50, required=True)
    person_address_postal_code = serializers.CharField(max_length=50, required=True)

    phone = serializers.CharField(max_length=50, required=True)
    identity_document = serializers.FileField(required=True)


class StripeConnectPayoutSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True)


class UserOnboardingRequirementStatusSerializer(serializers.Serializer):
    user_type = serializers.CharField(read_only=True)
    fleet_application = serializers.BooleanField(read_only=True)
    w9_information = serializers.BooleanField(read_only=True)
    service_agreement = serializers.BooleanField(read_only=True)
    stripe_onboarding_currently_due = serializers.BooleanField(read_only=True)
