import stripe

def create_user_account_stripe(email):
    stripe_customer_id = stripe.Account.create(
        type="custom",
        country="US",
        email=email,
        capabilities={"card_payments": {"requested": False}, "transfers": {"requested": True}},
    )
    return stripe_customer_id.get('id')
