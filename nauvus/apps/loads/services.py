import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.db import transaction

from nauvus.apps.carrier.models import CarrierUser
from nauvus.apps.loads.models import DeliveryDocument, Load
from nauvus.apps.payments.models import Invoice, LoadSettlement
from nauvus.services.credit.oatfi.api import Oatfi
from nauvus.services.stripe import StripeClient

logger = logging.getLogger(__name__)

oatfi_client = Oatfi()


def deliver_load(load: Load, delivery_date):
    """Marks the load as deliver and initiates the invoice

    Args:
        load (Load): The load that was delivered
        delivery_date (datetime): the timestamp of the delivery

    Raises:
        Exception: At least one delivery document must be present for a load to be delivered
    """

    # validate that there is at least one delivery document
    docs = DeliveryDocument.objects.filter(load_id=load.id)
    if len(docs) == 0:
        raise Exception("Cannot mark a load as delivered without delivery documents.")

    try:
        # determine the carrier user
        carrier = load.get_carrier()

        carrier_name = carrier.organization_name
        carrier_user = CarrierUser.objects.get(carrier=carrier)
        origin_city = load.origin.get("city")
        dest_city = load.destination.get("city")
        delivery_date_string = delivery_date.strftime("%Y-%m-%d")
        invoice_desc = (
            f"Delivery of load {load.id} from {origin_city} to {dest_city} on {delivery_date_string} by {carrier_name}"
        )
        amount_due = int(float(load.final_rate) * 100)  # cents
        stripe_payment_link = StripeClient().get_payment_link(amount_due, load.id)

        if not stripe_payment_link:
            raise Exception

        inv_due_date = datetime.now() + timedelta(days=30)

        nauvus_fee_percent = settings.NAUVUS_HANDLING_FEE_PERCENT
        nauvus_fee_in_cents = round(amount_due * (nauvus_fee_percent / 100))

        with transaction.atomic():
            load_settlement = LoadSettlement.objects.create(
                load=load, nauvus_fee_percent=nauvus_fee_percent, nauvus_fees_in_cents=nauvus_fee_in_cents
            )

            # create the invoice
            invoice = Invoice.objects.create(
                broker=load.broker,
                carrier_user=carrier_user,
                due_date=inv_due_date,
                load_settlement=load_settlement,
                amount_due_in_cents=amount_due,
                description=invoice_desc,
                stripe_payment_link=stripe_payment_link.get("url"),
                stripe_payment_id=stripe_payment_link.get("id"),
            )

            load.current_status = Load.Status.DELIVERED
            load.delivered_date = delivery_date
            load.save()

        oatfi_client.send_invoice_history([invoice])
        invoice.send()
    except Exception as e:
        # revert any objects in memory and clean up stripe if there is an issue
        logger.error(
            f"Encountered exception '{e}' while attempting to mark load as delivered. "
            + f" Load id {load.id} was not marked as delivered.",
            stack_info=True,
        )


def book_load(load: Load):
    """Executes any needed business logic when a load is booked

    Args:
        load (Load): The load to book
    """
    broker = load.broker
    oatfi_client.save_broker(broker)
