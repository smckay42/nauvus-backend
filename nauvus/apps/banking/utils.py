from nauvus.services.stripe import StripeClient


def get_files(file, purpose):

    """
    Create File Object For the stripe connect account.
    Returns file object created on Stripe
    """

    file_obj = StripeClient.create_files(file=file, purpose=purpose)
    return file_obj


def get_capabilities():

    """Capabilities in stripe connect account"""

    capabilities_obj = {
        # "card_payments": {"requested": True},
        "transfers": {"requested": True},
    }
    return capabilities_obj


def get_tos_acceptance(country="US"):

    """Tos acceptance in stripe connect account"""
    tos_acceptance = {
        "date": 1609798905,
        "ip": "8.8.8.8",
    }

    # TODO: Need to update logic, Need to ask frontend if they can manage this form from frontend
    if country != "US":
        tos_acceptance["service_agreement"] = "recipient"
    return tos_acceptance


def get_settings():

    """Settings in stirpe connect account."""

    settings = {"payments": {"statement_descriptor": "NAUVUS"}}

    return settings


def get_business_profile(name, description, mcc):

    """Business_profile For stripe account"""

    business_profile = {
        "name": name,
        "product_description": description,
        "mcc": mcc,
    }

    return business_profile


def get_company(
    name,
    phone,
    company_address_line1,
    company_address_line2,
    company_city,
    company_address_state,
    company_country,
    company_address_postal_code,
    structure=None,
    tax_id=None,
):

    """Company details for stripe account"""

    company = {
        "address": {
            "city": company_city,
            "country": company_country,
            "line1": company_address_line1,
            "line2": company_address_line2,
            "postal_code": company_address_postal_code,
            "state": company_address_state,
        },
        "name": name,
        "phone": phone,
        "structure": structure,
        "tax_id": tax_id,
        "directors_provided": "true",
        "executives_provided": "true",
        "owners_provided": "true",
    }

    return company


def get_external_account(
    country,
    currency,
    # account_holder_name,
    # account_holder_type,
    account_number,
    routing_number,
):

    """Bank account details for creating a connect account"""

    external_account = {
        "object": "bank_account",
        "country": country,
        "currency": currency,
        # "account_holder_name": account_holder_name,
        # "account_holder_type": account_holder_type,
        "account_number": account_number,
        "routing_number": routing_number,
    }
    return external_account


def get_relationship():

    """Relationship of person with company."""

    relationship = {
        "title": "ceo",
        "percent_ownership": 25,
        "representative": "true",
        "owner": "true",
    }

    return relationship


def get_dob(day, month, year):

    """DOB Information of connected person"""

    dob = {"day": day, "month": month, "year": year}
    return dob


def get_address(line1, line2, city, state, country, postal_code):

    """Address information of connected person"""

    address = {
        "line1": line1,
        "line2": line2,
        "city": city,
        "state": state,
        "country": country,
        "postal_code": postal_code,
    }

    return address


def get_verification(document):

    """Document For person's identity verification"""

    verification = {"document": {"front": document}}

    return verification
