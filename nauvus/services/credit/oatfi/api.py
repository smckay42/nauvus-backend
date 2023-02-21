import base64
import logging
from uuid import UUID

import httpx
from django.conf import settings

from nauvus.apps.broker.models import Broker
from nauvus.apps.carrier.models import CarrierUser
from nauvus.apps.payments.models import Invoice, Loan, Payment
from nauvus.services.stripe import StripeClient

logger = logging.getLogger("OATFI")
stripe_client = StripeClient()


class Oatfi:
    api_key = settings.OATFI_API_KEY
    url_base = settings.OATFI_URL
    partner_id = settings.OATFI_PARTNER_ID
    factoring_product_uuid = settings.OATFI_FACTORING_PRODUCT_ID

    def __new__(cls):

        encode_client = base64.b64encode(cls.api_key.encode())
        decode_client = encode_client.decode()

        # set up the header
        headers = {
            "Authorization": "Basic " + str(decode_client),
        }
        timeout = httpx.Timeout(10.0, connect=20.0, read=None)
        cls.client = httpx.Client(timeout=timeout, verify=False)
        cls.client.headers.update(headers)
        return object.__new__(cls)

    def __save_business(
        self,
        id,
        business_name: str,
        mc_number,
        email="none_provided@nauvus.com",
        contact_first_name="None",
        contact_last_name="None",
        street_address="None",
        city="None",
        state="GA",
        zip="00000",
        tax_id="000000000",
        stripe_acct_id="",
    ):
        """Creates a new oatfi business record with the given information.  If record is present already,
        then updates the record.

        Args:
            id : The id of the business within our system (e.g. the carrier uid)
            business_name : The name of the business
            business_address : the address of the business as a JSON object
            contact_email : the email of the company contact
            mc_number : The motor carrier (MC) number for the business

        Returns:
            ``200``, if successful.  Payload returns the ``id`` of the object sent to Oatfi.

            Sample payload::

                {"businesses": [{"externalId": "20c64a3d-71cb-4400-8225-6d19918aa183"}]}
        """

        url = f"{self.url_base}/business"

        # ensure that there is always some sort of email address sent to Oatfi
        contact_email = email
        if email is None or len(email) == 0:
            contact_email = "none_provided@nauvus.com"

        payload = {
            "name": business_name,
            "externalId": id,
            "metadata": {"mcNumber": mc_number},
            "contactEmail": contact_email,
            "contactFirstName": contact_first_name,
            "contactLastName:": contact_last_name,
            "streetAddress": street_address,
            "city": city,
            "state": state,
            "postalCode": zip,
            "taxId": tax_id,
            "paymentSettings": [{"type": "STRIPE", "data": {"account_id": stripe_acct_id}}],
        }

        try:
            self.get_business_information(id)

            response = self.client.put(url, json=payload)
        except Exception:
            # business wasn't found, so create a new one
            payload = {"businesses": [payload]}
            response = self.client.post(url, json=payload)

        if int(response.status_code) >= 400:
            raise Exception(f"Received {response.status_code}.  Full Response: {response.text}")

        # if no exception return True.
        return True

    def __get_business_id(self, business):
        biz_type = type(business)

        if biz_type is Broker:
            id = str(business.uid)
        elif biz_type is CarrierUser:
            id = str(business.carrier.uid)
        elif biz_type is str:
            id = business
        elif biz_type is UUID:
            id = str(business)
        else:
            raise Exception(f"Unable to get business id for {business}")

        return id

    def __get_preapproval(self, id):
        url = f"{self.url_base}/business/{id}/preapproval/{self.factoring_product_uuid}"

        response = self.client.get(url)

        if int(response.status_code) >= 400:
            raise Exception(f"Received {response.status_code}.  Full Response: {response.text}")

        preapproval_status = response.json()
        return preapproval_status["preapproved"]

    def __get_underwriting(self, id):
        url = f"{self.url_base}/business/{id}/underwrite/{self.factoring_product_uuid}"

        response = self.client.get(url)

        if response.status_code >= 400:
            raise Exception(f"No business found for id: {id}")

        return response.json()["creditLimit"]

    def __has_invoice(self, id):
        url = f"{self.url_base}/invoice/{id}/"

        response = self.client.get(url)

        if response.status_code >= 400:
            return False

        return True

    def save_broker(self, broker: Broker):
        """Adds a broker as a business to Oatfi.  If broker exists, updates the record.

        Args:
            broker (Broker): _description_

        Returns:
            True, if successful.  Throws an Exception otherwise.
        """

        self.__save_business(
            id=str(broker.uid),
            business_name=broker.name,
            mc_number=broker.mc_number,
            email=broker.email,
            contact_first_name=broker.contact_first_name,
            contact_last_name=broker.contact_last_name,
            street_address=broker.street1,
            city=broker.city,
            state=broker.state,
            zip=broker.zip_code,
        )

        return True

    def save_carrier(self, carrier_user: CarrierUser):

        carrier = carrier_user.carrier
        user = carrier_user.user

        # TODO: revisit this after reworking the carrier & user model
        self.__save_business(
            id=str(carrier.uid),
            business_name=carrier.organization_name,
            mc_number=carrier.mc_number,
            email=user.email,
            contact_first_name=user.first_name,
            contact_last_name=user.last_name,
            street_address=carrier.street1,
            city=carrier.city,
            state=carrier.state,
            zip=carrier.zip_code,
            stripe_acct_id=user.stripe_customer_id,
        )

        return True

    def send_invoice_history(self, invoices: list):

        url = f"{self.url_base}/invoice"
        invoice_array = []

        for invoice in invoices:
            temp = {
                "externalId": str(invoice.uid),
                "amount": invoice.amount_due_in_cents,
                "description": invoice.description,
                "invoiceApprovedByPayor": True,
                "payorExternalId": str(invoice.broker.uid),
                "payeeExternalId": str(invoice.carrier_user.carrier.uid),
                "dueDate": invoice.due_date_in_milliseconds(),
                "invoiceDate": invoice.created_at_in_milliseconds(),
            }

            if invoice.paid_date is not None:
                temp["paymentDate"] = invoice.paid_date_in_milliseconds()

            # if the invoice is already at Oatfi, then update it
            if self.__has_invoice(invoice.uid) is False:
                invoice_array.append(temp)
            else:
                response = self.client.put(url, json=temp)
                if int(response.status_code) >= 400:
                    raise Exception(f"Received {response.status_code}.  Full Response: {response.text}")

        if len(invoice_array) > 0:

            payload = {"invoices": invoice_array}

            response = self.client.post(url, json=payload)

            if int(response.status_code) >= 400:
                raise Exception(f"Received {response.status_code}.  Full Response: {response.text}")

        return True

    def get_broker_preapproval(self, broker: Broker):

        preapproval = self.__get_preapproval(str(broker.uid))
        logger.debug(f"Pre-approval for broker {broker.name} (uid: {broker.uid} is {preapproval}")
        return preapproval

    def get_loan_offer(self, invoice: Invoice) -> Loan:

        url = f"{self.url_base}/loan/offer"

        broker_id = str(invoice.broker.uid)
        carrier_id = str(invoice.carrier_user.carrier.uid)

        # first get preapproval for broker and carrier
        broker_preapproval = self.__get_preapproval(broker_id)
        carrier_preapproval = self.__get_preapproval(carrier_id)

        if not (broker_preapproval and carrier_preapproval):
            # if the carrier and broker are not pre-approved, then do NOT return a loan offer
            return None

        # check for underwriting
        credit_limit = self.__get_underwriting(carrier_id)

        if credit_limit <= 0:
            # if there is no credit, do not return a loan
            return None

        # check for a loan offer for the carrier
        payload = {
            "productUUID": self.factoring_product_uuid,
            "businessExternalId": carrier_id,
        }

        response = self.client.post(url, json=payload)

        if int(response.status_code) >= 401:
            raise Exception(f"Received {response.status_code}.  Full Response: {response.text}")

        invoices = response.json()["invoices"]

        loan_details = [item for item in invoices if item.get("externalId") == str(invoice.uid)]

        if loan_details.count == 0:
            return None

        loan_details = loan_details[0]

        loan = Loan()
        loan.current_status = Loan.Status.OFFERED
        loan.lender = Loan.Source.OATFI
        loan.invoice = invoice
        loan.principal_amount_in_cents = loan_details["principalAmount"]
        loan.fee_amount_in_cents = loan_details["feeAmount"]
        loan.terms = loan_details["termsLink"]

        # parse the result and create a loan for the invoice that was passed in
        return loan

    def accept_loan(self, loan: Loan) -> Payment:

        invoice = loan.invoice
        url = f"{self.url_base}/loan/funding"

        amount_in_cents = loan.principal_amount_in_cents

        payload = {
            "productUUID": self.factoring_product_uuid,
            "amount": amount_in_cents,
            "businessExternalId": str(invoice.carrier_user.carrier.uid),
            "invoiceExternalId": str(invoice.uid),
        }

        response = self.client.post(url, json=payload)

        if int(response.status_code) >= 400:
            raise Exception(f"Received {response.status_code}.  Full Response: {response.text}")

        loan.current_status = Loan.Status.OUTSTANDING

        details = response.json()
        loan.lender_loan_id = details["loanId"]
        loan.save()

        # create the payment and reference the transfer
        payment = Payment.objects.create(
            payment_type=Payment.PaymentType.LOAN_PAYOUT,
            amount_in_cents=amount_in_cents,
            load_settlement=loan.invoice.load_settlement,
            stripe_ref_id=details.get("transactionId", "None"),
        )

        return payment

    def repay_loan(self, loan: Loan) -> Payment:
        """Transfer loan principal and fees to Oatfi via Stripe and send a payload
        with the information in order to get the loan closed out.
        """
        # start by initiating a transfer to oatfi
        url = f"{self.url_base}/payment"

        transfer_amount = loan.fee_amount_in_cents + loan.principal_amount_in_cents
        transfer_msg = f"Repayment of loan {loan.uid} for {loan.invoice.load_settlement.load.id}"
        stripe_transfer = stripe_client.create_transfer(transfer_amount, settings.OATFI_STRIPE_ACCOUNT, transfer_msg)

        transfer_id = stripe_transfer["id"]

        invoice = loan.invoice

        payload = {
            "productUUID": self.factoring_product_uuid,
            "businessExternalId": str(invoice.carrier_user.carrier.uid),
            "invoiceExternalId": str(loan.invoice.uid),
            "transferId": transfer_id,
            "amount": transfer_amount,
        }

        response = self.client.post(url, json=payload)
        if int(response.status_code) >= 400:
            raise Exception(f"Received {response.status_code}.  Full Response: {response.text}")

        # create the payment and reference the transfer
        payment = Payment.objects.create(
            payment_type=Payment.PaymentType.LOAN_REPAYMENT,
            amount_in_cents=transfer_amount,
            load_settlement=loan.invoice.load_settlement,
            stripe_ref_id=transfer_id,
        )

        return payment

    def get_invoices(self, business) -> list:
        id = self.__get_business_id(business)

        url = f"{self.url_base}/business/{id}/invoices"

        response = self.client.get(url)

        # TODO: make this return invoice objects
        return response

    def get_business_information(self, business):

        id = self.__get_business_id(business)

        url = f"{self.url_base}/business/{id}"

        response = self.client.get(url)

        if response.status_code >= 400:
            # business was not found, raise an exception
            # TODO: subclass this exception
            raise Exception(f"No business found for id: {id}")

        return response.json()

    def update_invoice(self, invoice: Invoice):
        url = f"{self.url_base}/invoice"

        payload = {
            "externalId": str(invoice.uid),
        }

        if invoice.paid_date is not None:
            payload["paymentDate"] = invoice.paid_date_in_milliseconds()

        response = self.client.put(url, json=payload)

        if int(response.status_code) >= 400:
            logger.error(f"OATFI Error: {response.text}")
            raise Exception(f"Received {response.status_code}.  Full Response: {response.text}")

        return True
