import stripe
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from nauvus.api.permissions import IsCarrier
from nauvus.apps.carrier.models import (
    CarrierFleetApplication,
    CarrierServiceAgreement,
    CarrierUser,
    CarrierW9Information,
)
from nauvus.apps.payments.services import get_unpaid_invoices_balance_in_cents
from nauvus.services.stripe import StripeClient

from ...dispatcher.models import DispatcherServiceAgreement, DispatcherUser, DispatcherW9Information
from ...driver.models import Driver, DriverServiceAgreement
from .serializers import StripeCreateAccountLinkSerializer, UserOnboardingRequirementStatusSerializer

stripe_client = StripeClient()


class StripeCreateAccountLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StripeCreateAccountLinkSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):

            refresh_url = serializer.validated_data.get("refresh_url")
            return_url = serializer.validated_data.get("return_url")
            account = request.user.stripe_customer_id

            try:
                stripe_account_link = stripe.AccountLink.create(
                    account=account,
                    refresh_url=refresh_url,
                    return_url=return_url,
                    type="account_onboarding",
                    collect="eventually_due",
                )
                return Response(data=stripe_account_link, status=status.HTTP_200_OK)
            except stripe.error.InvalidRequestError as e:
                raise NotFound(e.user_message)
            except Exception:
                return Response({"message": "Something else happened, completely unrelated to Stripe"})


class UserOnboardingRequirementStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user_type = request.user.user_type

        user_stripe_id = request.user.stripe_customer_id

        onboarding_requirements_status = {}

        if user_type == "carrier_owner":
            try:
                api_response = stripe.Account.retrieve(user_stripe_id)
                stripe_requirements_response = api_response.get("requirements").get("currently_due")

                # If there are any currently_due requirements, returns False.
                # If all requirements are completed, returns True
                stripe_requirements = True
                if stripe_requirements_response:
                    stripe_requirements = False

            except stripe.error.PermissionError:
                return Response(data={"message": "Stripe Permission Error"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                return Response(
                    {"message": "Something else happened, completely unrelated to Stripe."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            carrier_user = CarrierUser.objects.get(user=self.request.user)

            fleet = CarrierFleetApplication.objects.filter(carrier=carrier_user.carrier).exists()
            w9 = CarrierW9Information.objects.filter(carrier=carrier_user.carrier).exists()
            service_agreement = (
                CarrierServiceAgreement.objects.filter(carrier=carrier_user.carrier).filter(is_signed=True).exists()
            )

            onboarding_requirements_status["user_type"] = user_type
            onboarding_requirements_status["fleet_application"] = fleet
            onboarding_requirements_status["w9_information"] = w9
            onboarding_requirements_status["service_agreement"] = service_agreement
            onboarding_requirements_status["stripe_onboarding_currently_due"] = stripe_requirements

        if user_type == "dispatcher":
            dispatcher_user = DispatcherUser.objects.get(user=self.request.user)
            w9 = DispatcherW9Information.objects.filter(dispatcher=dispatcher_user.dispatcher).exists()
            service_agreement = (
                DispatcherServiceAgreement.objects.filter(dispatcher=dispatcher_user.dispatcher)
                .filter(is_signed=True)
                .exists()
            )

            onboarding_requirements_status["user_type"] = user_type
            onboarding_requirements_status["w9_information"] = w9
            onboarding_requirements_status["service_agreement"] = service_agreement

        if user_type == "driver":
            driver_user = Driver.objects.get(user=self.request.user)
            service_agreement = (
                DriverServiceAgreement.objects.filter(driver=driver_user).filter(is_signed=True).exists()
            )

            onboarding_requirements_status["user_type"] = user_type
            onboarding_requirements_status["service_agreement"] = service_agreement

        serializer = UserOnboardingRequirementStatusSerializer(onboarding_requirements_status)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CarrierBankingBalanceView(APIView):

    permission_classes = [IsAuthenticated & IsCarrier]

    def get(self, request):
        """Returns the balance for the carrier including both the current balance as well as the
        pending balance
        """
        user = request.user

        carrier_user = CarrierUser.objects.get(user=user)

        unpaid_invoice_balance = get_unpaid_invoices_balance_in_cents(carrier_user)
        stripe_balance = stripe_client.retrieve_balance(user.stripe_customer_id)

        response_payload = {
            "current_balance": (stripe_balance / 100),
            "pending_balance": (unpaid_invoice_balance / 100),
        }

        return Response(response_payload, status=status.HTTP_200_OK)


class CarrierAccountDetailsView(APIView):

    permission_classes = [IsAuthenticated & IsCarrier]

    def get(self, request):
        """Returns the external bank name and last four of account number."""

        user = request.user

        account_info = stripe_client.get_external_account_info(user.stripe_customer_id)

        return Response(account_info, status=status.HTTP_200_OK)
