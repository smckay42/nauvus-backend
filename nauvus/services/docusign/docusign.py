import requests
from django.conf import settings
from docusign_esign import ApiClient, EnvelopeDefinition, EnvelopesApi, TemplateRole

from nauvus.apps.carrier.models import CarrierServiceAgreement, CarrierUser
from nauvus.apps.dispatcher.models import Dispatcher, DispatcherServiceAgreement, DispatcherUser
from nauvus.apps.driver.models import Driver, DriverServiceAgreement
from nauvus.services.docusign import tokens


def create_jwt_grant_token():
    token = tokens.docusign_token()
    url = "https://account-d.docusign.com/oauth/token"
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": token,
    }

    response = requests.post(url, data=data)
    response_data = response.json()
    access_token = response_data.get("access_token")
    return access_token


def make_envelope(signer):
    """
    Creates envelope
    args -- parameters for the envelope:
    signer_email, signer_name, signer_client_id
    returns an envelope definition
    """
    args = {
        "template_id": settings.DOCUSIGN_TEMPLATE_ID,
        "signer_email": signer.email,
        "signer_name": "{} {}".format(signer.first_name, signer.last_name),
    }

    # Create the envelope definition
    envelope_definition = EnvelopeDefinition(
        status="sent",
        template_id=args["template_id"],  # requests that the envelope be created and sent.
    )
    # Create template role elements to connect the signer and cc recipients
    # to the template
    signer = TemplateRole(
        email=args["signer_email"],
        name=args["signer_name"],
        role_name="signer",
    )
    # Add the TemplateRole objects to the envelope object
    envelope_definition.template_roles = [signer]
    return envelope_definition


def docusign_worker(signer):
    """
    Create the envelope request object
    Send the envelope
    """
    args = {
        "base_path": settings.DOCUSIGN_BASE_PATH,
        "ds_access_token": create_jwt_grant_token(),
        "account_id": settings.DOCUSIGN_ACCOUNT_ID,
    }

    # envelope_args = args["envelope_args"]
    # Create the envelope request object
    envelope_definition = make_envelope(signer)
    # Call Envelopes::create API method
    # Exceptions will be caught by the calling function
    api_client = ApiClient()
    api_client.host = args["base_path"]
    api_client.set_default_header("Authorization", "Bearer " + args["ds_access_token"])
    envelope_api = EnvelopesApi(api_client)
    results = envelope_api.create_envelope(args["account_id"], envelope_definition=envelope_definition)
    envelope_id = results.envelope_id
    try:
        carrier_user = CarrierUser.objects.get(user=signer)
        carrier_service_agreement = CarrierServiceAgreement()
        carrier_service_agreement.carrier = carrier_user.carrier
        carrier_service_agreement.envelope_id = envelope_id
        carrier_service_agreement.is_signed = False
        carrier_service_agreement.save()

    except CarrierUser.DoesNotExist:
        try:
            dispatcher_user = DispatcherUser.objects.get(user=signer)
            dispatcher_service_agreement = DispatcherServiceAgreement()
            dispatcher_service_agreement.dispatcher = dispatcher_user.dispatcher
            dispatcher_service_agreement.envelope_id = envelope_id
            dispatcher_service_agreement.is_signed = False
            dispatcher_service_agreement.save()

        except Dispatcher.DoesNotExist:
            driver_user = Driver.objects.get(user=signer)
            driver_service_agreement = DriverServiceAgreement()
            driver_service_agreement.driver = driver_user
            driver_service_agreement.envelope_id = envelope_id
            driver_service_agreement.is_signed = False
            driver_service_agreement.save()

    return {"envelope_id": envelope_id}
