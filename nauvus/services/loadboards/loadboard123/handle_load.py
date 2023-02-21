import logging
from decimal import Decimal

from dateutil import parser

from nauvus.apps.loads.models import Load
from nauvus.utils.location import Location

logger = logging.getLogger("123Loadboard")


class Loadboard123Load:
    @staticmethod
    def normalize_load(raw_load, broker, existing_load: Load = None) -> Load:

        if existing_load:
            return_load = existing_load
        else:
            return_load = Load()

        origin_latitude = raw_load.get("originLocation").get("geolocation").get("latitude", "")
        origin_longitude = raw_load.get("originLocation").get("geolocation").get("longitude", "")
        origin_adress1 = raw_load.get("originLocation").get("address").get("addressLine1")
        origin_adress2 = raw_load.get("originLocation").get("address").get("addressLine2")
        origin_city = raw_load.get("originLocation").get("address").get("city")
        origin_state = raw_load.get("originLocation").get("address").get("state")
        origin_zipcode = raw_load.get("originLocation").get("address").get("zipCode")

        if not origin_zipcode:
            if origin_latitude and origin_longitude:
                origin_zipcode = Location().get_zipcode_by_coordinates(origin_latitude, origin_longitude)
            else:
                origin_zipcode = Location().get_zipcode_by_city_state(origin_city, origin_state)

        origin = {
            "address1": origin_adress1,
            "address2": origin_adress2,
            "city": origin_city,
            "state": origin_state,
            "zipcode": origin_zipcode,
            "longitude": origin_longitude,
            "latitude": origin_latitude,
        }

        destination_latitude = raw_load.get("destinationLocation").get("geolocation").get("latitude", "")
        destination_longitude = raw_load.get("destinationLocation").get("geolocation").get("longitude", "")
        destination_adress1 = raw_load.get("destinationLocation").get("address").get("addressLine1")
        destination_adress2 = raw_load.get("destinationLocation").get("address").get("addressLine2")
        destination_city = raw_load.get("destinationLocation").get("address").get("city")
        destination_state = raw_load.get("destinationLocation").get("address").get("state")
        destination_zipcode = raw_load.get("destinationLocation").get("address").get("zipCode")

        if not destination_zipcode:
            if destination_latitude and destination_longitude:
                destination_zipcode = Location().get_zipcode_by_coordinates(destination_latitude, destination_longitude)
            else:
                destination_zipcode = Location().get_zipcode_by_city_state(destination_city, destination_state)

        destination = {
            "address1": destination_adress1,
            "address2": destination_adress2,
            "city": destination_city,
            "state": destination_state,
            "zipcode": destination_zipcode,
            "longitude": destination_longitude,
            "latitude": destination_latitude,
        }

        pickup_date = parser.parse(raw_load.get("pickupDateTimesUtc")[-1])

        dropoff_date = None
        if raw_load.get("deliveryDateTimeUtc", None) is not None:
            try:
                dropoff_date = parser.parse(raw_load.get("deliveryDateTimeUtc")[-1])
            except parser.ParserError as e:
                logger.info(f"{e}")
                return None

        current_status = "available"

        weight = raw_load.get("weight")
        commodity = raw_load.get("commodity")
        length = raw_load.get("length")
        trailer_type = raw_load.get("equipments")[-1].get("equipmentType")
        details = {"weight": weight, "commodity": commodity, "length": length, "trailer_type": trailer_type}

        contact_details = {"name": "", "phone": "", "email": "", "reference_number": raw_load.get("id"), "notes": ""}

        posted_rate = 0.00
        if raw_load.get("rate", None) is not None:
            posted_rate = Decimal(raw_load.get("rate").get("amount"))

        if not origin_zipcode or not destination_zipcode:
            return None

        mileage = raw_load.get("mileage")
        ref_title = raw_load.get("postReferece")
        if not ref_title:
            pu_dt = pickup_date.strftime("%Y-%m-%d")
            ref_title = f"{origin_city} to {destination_city} on  {pu_dt}"

        return_load.origin = origin

        return_load.destination = destination
        return_load.pickup_date = pickup_date
        return_load.dropoff_date = dropoff_date
        return_load.current_status = current_status
        return_load.broker = broker
        return_load.details = details
        return_load.contact = contact_details
        return_load.posted_rate = posted_rate
        return_load.estimated_mileage = mileage
        return_load.reference_title = ref_title

        return return_load
