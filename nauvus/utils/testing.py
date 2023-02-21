import random
import string

from nauvus.apps.payments.models import Invoice


def __id_generator(size=12, chars=string.ascii_letters + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def create_stripe_checkout_session_event(invoice: Invoice, event_type, event_time, session_id, payment_intent_id):
    total = invoice.amount_due_in_cents

    load_id = invoice.load_settlement.load.id
    payment_intent = payment_intent_id
    payment_link_id = invoice.stripe_payment_id
    checkout_session_id = session_id

    if event_type == "checkout.session.completed":
        payment_status = "unpaid"
    elif event_type == "checkout.session.async_payment_succeeded":
        payment_status = "paid"
    else:
        # for now default to unpaid
        payment_status = "unpaid"

    obj = {
        "object": {
            "id": checkout_session_id,
            "object": "checkout.session",
            "amount_subtotal": total,
            "amount_total": total,
            "cancel_url": "https://stripe.com",
            "created": event_time,
            "currency": "usd",
            "customer_details": {
                "email": invoice.broker.email,
                "name": f"{invoice.broker.contact_first_name} {invoice.broker.contact_last_name}",
            },
            "expires_at": event_time + 100000000,
            "locale": "auto",
            "metadata": {"load_id": str(load_id)},
            "mode": "payment",
            "payment_intent": payment_intent,
            "payment_link": payment_link_id,
            "payment_method_collection": "always",
            "payment_method_options": {"us_bank_account": {"verification_method": "automatic"}},
            "payment_method_types": ["us_bank_account"],
            "payment_status": payment_status,
            "status": "complete",
            "submit_type": "auto",
            "success_url": "https://stripe.com",
            "total_details": {"amount_discount": 0, "amount_shipping": 0, "amount_tax": 0},
        }
    }

    event_id = "evt_test_" + __id_generator(size=24)
    event = {
        "id": event_id,
        "object": "event",
        "api_version": "2020-08-27",
        "created": event_time,
        "data": obj,
        "pending_webhooks": 0,
        "request": {"id": "req_fttcwjxRtciYTM", "idempotency_key": "0d83611e-1e00-4ce6-aa3e-5d34f9d73ab4"},
        "type": event_type,
    }

    return event
