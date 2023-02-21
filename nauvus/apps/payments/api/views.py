import logging

import stripe
from django.shortcuts import get_object_or_404
from rest_framework import status, views
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from nauvus.api.permissions import IsDelivered, IsLoadCarrier
from nauvus.apps.loads.models import Load
from nauvus.apps.payments.api.serializers import PaymentTermsSerializer, TransferUserMoneyToExternalAccountSerializer
from nauvus.apps.payments.models import Invoice
from nauvus.services.credit.oatfi.api import Oatfi

oatfi = Oatfi()
logger = logging.getLogger(__name__)


class LoadPaymentViewSet(ViewSet):
    permission_classes = [IsDelivered & IsLoadCarrier]

    def get_serializer_class(self):
        if self.action == "accept_payment_terms":
            return PaymentTermsSerializer
        return super().get_serializer_class()

    def get_object(self):
        load = get_object_or_404(Load, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, load)
        return load

    def __get_instant_payment_details(self, invoice):

        loan = oatfi.get_loan_offer(invoice)
        loan.save()

        fees = (loan.fee_amount_in_cents + invoice.load_settlement.nauvus_fees_in_cents) / 100
        available_today = loan.principal_amount_in_cents / 100

        available_later = round(float(invoice.load_settlement.load.final_rate) - available_today - fees, 2)

        payment_details = {
            "available_today": available_today,
            "available_on_broker_payment": available_later,
            "fees": fees,
            "total": invoice.load_settlement.load.final_rate,
            "terms_link": loan.terms,
        }

        return payment_details

    def __accept_instant_payment_terms(self, load_settlement):

        payment = oatfi.accept_loan(load_settlement.invoice.loan)

        return {"payment_id": payment.uid}

    @action(detail=True, methods=["get"], url_path="types")
    def get_available_payment_types(self, request, pk):
        load = self.get_object()

        try:
            instant_pay_preapproval = oatfi.get_broker_preapproval(load.broker)
        except Exception:
            logger.debug(
                f"Encountered exception getting pre-approval for {load.broker.name}. Force pre-approval to False",
                stack_info=True,
            )
            instant_pay_preapproval = False

        payment_types = {"instant": instant_pay_preapproval}
        logger.debug(f"instant pay approval for load {load.id} is {instant_pay_preapproval}")

        return Response(
            payment_types,
        )

    @action(detail=True, methods=["get"], url_path="details")
    def get_payment_details(self, request, pk):
        load = self.get_object()

        load_settlement = load.loadsettlement

        # send the invoice history even if the user does not do instant payment
        invoice = Invoice.objects.get(load_settlement=load_settlement)
        oatfi.send_invoice_history([invoice])

        instant_payment = request.query_params.get("instant")

        if instant_payment is not None and instant_payment.lower() == "true":
            return Response(self.__get_instant_payment_details(invoice))

        fees = load_settlement.nauvus_fees_in_cents / 100

        available_later = round(float(load_settlement.load.final_rate) - fees, 2)

        payment_details = {
            "available_today": 0,
            "available_on_broker_payment": available_later,
            "fees": fees,
            "total": load.final_rate,
            "terms_link": "http://terms",
        }  # TODO: replace terms link with a real terms link
        return Response(payment_details, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="accept",
    )
    def accept_payment_terms(self, request, pk):
        """Accepts the payment terms and initiates any transfers.

        If the terms are not accepted or no timestamp is provided, this will error out

        Payload:
        {
            "instant": true | false,
            "terms_accepted": true | false.
            "terms_accepted_timestamp": <timestamp>
        }

        """
        load = self.get_object()

        serializer = PaymentTermsSerializer(data=request.data, context={"load": load})

        serializer.is_valid(raise_exception=True)

        load.current_status = Load.Status.PARTIAL_SETTLED
        load_settlement = load.loadsettlement

        load_settlement.accept_terms(serializer.validated_data["terms_accepted_timestamp"])

        # if instant pay, accept the loan with oatfi and do the payment
        # if not instant pay, accept the terms and do nothing else
        instant_payment = serializer.validated_data["instant"]
        if instant_payment:
            response = Response(self.__accept_instant_payment_terms(load_settlement), status=status.HTTP_200_OK)
            load_settlement.invoice.loan.save()
        else:
            response = Response(status=status.HTTP_200_OK)

        # save at the end to ensure that all the steps are completed
        load.save()
        load_settlement.save()

        return response


class TransferUserMoneyToExternalAccount(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransferUserMoneyToExternalAccountSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.request.user.stripe_customer_id
        amount = serializer.data.get("amount")

        amount_in_cents = int(float(amount) * 100)

        try:
            payout = stripe.Payout.create(
                amount=amount_in_cents,
                currency="usd",
                stripe_account=user,
            )
            return Response(data=payout, status=status.HTTP_200_OK)
        except Exception as err:
            return Response({"error": err.code}, status=status.HTTP_400_BAD_REQUEST)
