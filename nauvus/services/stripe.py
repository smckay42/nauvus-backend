import logging

import stripe
from django.conf import settings

logger = logging.getLogger("stripe")


class StripeClient(object):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    class EventTypes:
        CHECKOUT_SESSION_COMPLETED = "checkout.session.completed"
        CHECKOUT_SESSION_ASYNC_PAYMENT_SUCCEEDED = "checkout.session.async_payment_succeeded"

    # Customers
    @staticmethod
    def create_customer(email, name):
        """Create stripe customer"""
        return stripe.Customer.create(
            email=email,
            name=name,
        )

    # Bank Account
    @staticmethod
    def create_bank_account(
        customer_id,
        object,
        country,
        currency,
        account_holder_name,
        account_holder_type,
        account_number,
        routing_number,
    ):
        """Create customer bank account in stripe"""
        return stripe.Customer.create_source(
            customer_id,
            source={
                "object": object,
                "country": country,
                "currency": currency,
                "account_holder_name": account_holder_name,
                "account_holder_type": account_holder_type,
                "account_number": account_number,
                "routing_number": routing_number,
            },
        )

    # External Bank Account
    @staticmethod
    def create_external_bank_account(
        customer_id,
        object,
        country,
        currency,
        account_holder_name,
        account_holder_type,
        account_number,
        routing_number,
    ):
        """Create external bank account in stripe"""
        return stripe.Account.create_external_account(
            customer_id,
            external_account={
                "object": object,
                "country": country,
                "currency": currency,
                "account_holder_name": account_holder_name,
                "account_holder_type": account_holder_type,
                "account_number": account_number,
                "routing_number": routing_number,
            },
        )

    # Connected Account
    @staticmethod
    def create_account(
        type,
        country,
        # currency,
        # email,
        capabilities,
        tos_acceptance,
        business_type,
        # company,
        settings,
        business_profile,
        external_account,
    ):
        """Create stripe connect acccount"""
        return stripe.Account.create(
            type=type,
            country=country,
            # currency=[currency],
            capabilities=capabilities,
            tos_acceptance=tos_acceptance,
            business_type=business_type,
            settings=settings,
            business_profile=business_profile,
            # company=company,
            # email=email,
            external_account=external_account,
        )

    @staticmethod
    def create_person(
        id,
        id_number,
        first_name,
        last_name,
        email,
        relationship,
        dob,
        address,
        # ssn_last_4,
        # sin=None,
        phone=None,
        verification=None,
    ):

        """Create person in stripe"""
        return stripe.Account.create_person(
            id=id,
            id_number=id_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            relationship=relationship,
            dob=dob,
            address=address,
            phone=phone,
            verification=verification,
        )

    # Transfers
    @staticmethod
    def create_transfer(amount_in_cents, destination_account, description=""):
        """Create stripe transfer"""
        return stripe.Transfer.create(
            amount=amount_in_cents, currency="usd", destination=destination_account, description=description
        )

    @staticmethod
    def retrieve_transfer(transfer_id):
        """retrieve stripe transfer"""
        return stripe.Transfer.retrieve(
            transfer_id,
        )

    # Files
    @staticmethod
    def create_files(file, purpose):
        """Create stripe files"""
        return stripe.File.create(file=file, purpose=purpose)

    @staticmethod
    def retrieve_files(file_id):
        "retrive stripe files"
        return stripe.File.retrieve(
            file_id,
        )

    @staticmethod
    def retrieve_balance(stripe_account_id):
        """retrieve stripe balance"""
        balance = stripe.Balance.retrieve(stripe_account=stripe_account_id)

        balance_amount_in_cents = 0
        if balance:

            # get the available balance for the account
            available_balance = balance.get("available")

            for balance_type in available_balance:
                balance_amount_in_cents += balance_type.get("amount")

        return balance_amount_in_cents

    @staticmethod
    def retrieve_connect_account(stripe_id):
        """retrieve connect account"""
        return stripe.Account.retrieve(stripe_id)

    @staticmethod
    def retrieve_connect_account_balance(stripe_id):
        """retrieve connect account balance"""
        return stripe.Balance.retrieve(stripe_account=stripe_id)

    @staticmethod
    def create_payout(amount):
        """create payout to bank"""
        return stripe.Payout.create(amount=amount, currency="usd")

    @staticmethod
    def set_payout_manually(stripe_id):
        """set payout manually"""
        return stripe.Account.modify(
            stripe_id,
            settings={"payouts": {"schedule": {"interval": "manual"}}},
        )

    @staticmethod
    def tos_acceptance(stripe_id):
        """set tos acceptance"""
        return stripe.Account.modify(stripe_id, metadata={"internal_id": "42"})

    @staticmethod
    def standard_payout(amount, stripe_id):
        """instant payout"""
        return stripe.Payout.create(
            amount=int(amount) * 100,
            currency="usd",
            # method="instant",
            stripe_account=stripe_id,
        )

    @staticmethod
    def retrieve_payout(payout_id):
        "retrieve payout"
        return stripe.Payout.retrieve(payout_id)

    # list external accounts
    @staticmethod
    def get_all_external_accounts(stripe_id):
        """list all external account"""
        return stripe.Account.list_external_accounts(
            stripe_id,
            object="bank_account",
            # limit=3,
        )

    # list external accounts
    @staticmethod
    def get_external_account_info(stripe_id):
        """Get the bank name and last 4 of the account number"""
        ext_account = stripe.Account.list_external_accounts(
            stripe_id,
            object="bank_account",
        ).data[0]

        account_info = {"bank_name": ext_account.get("bank_name"), "account_num_last4": ext_account.get("last4")}
        return account_info

    # get external account
    @staticmethod
    def get_external_accounts(stripe_id, external_account_id):
        """get external account"""
        return stripe.Account.retrieve_external_account(
            stripe_id,
            external_account_id,
        )

    @staticmethod
    def get_payment_link(price, load_id):
        """create a payment link in stripe with the price of the load

        Returns None if there is an exception
        """
        try:
            stripe_price = stripe.Price.create(
                currency="usd",
                unit_amount=price,
                product=settings.STRIPE_PRODUCT_ID,
                metadata={"load_id": f"{load_id}"},
            )
            stripe_price_id = stripe_price.get("id")
            stripe_payment_link = stripe.PaymentLink.create(
                line_items=[{"price": stripe_price_id, "quantity": 1}],
                payment_method_types=["us_bank_account"],
                metadata={"load_id": f"{load_id}"},
            )
            return stripe_payment_link
        except Exception as e:
            logger.error(f"Unable to create payment link for load {load_id} due to error", e)
            return None

    @staticmethod
    def get_payment_intent(price, load_id):
        intent = stripe.PaymentIntent.create(
            amount=price,
            currency="usd",
            payment_method_types=["us_bank_account"],
            description=f"Delivery Load - {load_id}",
        )
        return intent

    @staticmethod
    def archive_price(price_id):
        try:
            stripe.Price.modify(price_id, active=False)
            logger.info(f"Price {price_id} archived.")
        except IndexError:
            logger.info(f"Price {price_id} not found.")

    @staticmethod
    def get_price_id_from_checkout_session(session_id):
        items = stripe.checkout.Session.retrieve(session_id, expand=["line_items"])
        price_id = items["line_items"]["data"][0]["price"]["id"]
        return price_id

    @staticmethod
    def archive_paymentlink(link_id):
        try:
            stripe.PaymentLink.modify(link_id, active=False)
            logger.info(f"PaymentLink {link_id} archived.")
        except IndexError:
            logger.info(f"PaymentLink {link_id} not found.")

    @staticmethod
    def construct_event(payload, sig_header, endpoint_secret):
        return stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
