from enum import Enum
from importlib import import_module

import httpx

from ..broker.models import Broker
from .models import Load


class LoadboardsEnum(Enum):
    LOADBOARD_123 = {
        "path": "nauvus.services.loadboards.loadboard123.api",
        "class_name": "Loadboard123",
    }


def get_loadboard(source_name):
    loadboard = LoadboardsEnum[source_name].value
    loadboard_path = loadboard.get("path")
    class_name = loadboard.get("class_name")
    loadboard_class = getattr(import_module(loadboard_path), class_name)
    return loadboard_class()


def update_contact_broker(source_name, load_id, broker_id, external_load_id):
    # Get the Loadboard class
    loadboard_class = get_loadboard(source_name)

    try:
        load_details = loadboard_class.get_load_details(external_load_id)

        name = load_details.get("dispatchName")
        phone = load_details.get("dispatchPhone").get("number")
        email = load_details.get("dispatchEmail")
        reference_number = load_details.get("id")

        contact_details = {
            "name": name,
            "phone": phone,
            "email": email,
            "reference_number": reference_number,
            "notes": "",
        }

        broker_phone = load_details.get("poster").get("phone").get("number")
        dot_number = load_details.get("poster").get("usdotNumber")
        Broker.objects.filter(id=broker_id).update(phone=broker_phone, dot_number=dot_number)

        Load.objects.filter(id=load_id).update(contact=contact_details)
    except AttributeError:
        pass


def get_broker_from_fmcsa(mc_number):
    web_key = "395a3001adecbd30bc0c1e8e1b4cc0e13a38babd"
    url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_number}/?webKey={web_key}"

    response = httpx.get(url)

    # Justin - I commented this out for now.
    # response_broker = response.json().get("content")[0].get("carrier")

    # broker_fields = {
    #     "name": response_broker.get("legalName"),
    #     "dot_number": str(response_broker.get("dotNumber")),
    #     "mc_number": str(mc_number),
    # }

    return response


def weight_converter(weight_value=None, from_unit=None, to_unit=None):
    if weight_value is None:
        return None

    if from_unit == "pound" and to_unit == "lbs":
        return weight_value
