import base64
import logging
import time
import uuid

import httpx
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from nauvus.apps.broker.models import Broker
from nauvus.apps.loads.models import AccessToken, Load, LoadSource
from nauvus.services.credit.oatfi.api import Oatfi

from .handle_load import Loadboard123Load

oatfi = Oatfi()

logger = logging.getLogger("123Loadboard")
US_STATES = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
]


class Loadboard123:
    def __init__(self):
        self.loadboard_username = settings.LOADBOARD_USERNAME
        self.loadboard_password = settings.LOADBOARD_PASSWORD
        self.loadboard_client_id = settings.LOADBOARD_CLIENT_ID
        self.loadboard_client_secret = settings.LOADBOARD_CLIENT_SECRET
        self.base_url = settings.LOADBOARD_URL

        self.loadboard_name = "LOADBOARD_123"
        self.token_max_time = 30

        headers = {
            "User-Agent": "Nauvus TMP Pro/1.47.2(nauvus@nauvus.com)",
            "123LB-Api-Version": "1.3",
        }
        timeout = httpx.Timeout(10.0, connect=20.0, read=None)
        self.client = httpx.Client(timeout=timeout, verify=False)
        self.client.headers.update(headers)

    def get_authorization_code(self):

        state = str(uuid.uuid4())

        url = self.base_url + "/authorize"

        query = {
            "response_type": "code",
            "client_id": self.loadboard_client_id,
            "redirect_uri": self.base_url + "/tokenreceiver",
            "scope": "offline_access",
            "state": state,
            "login_hint": self.loadboard_username,
        }

        try:
            response_redirect = self.client.get(url, params=query, follow_redirects=True)
        except httpx.ConnectTimeout as e:
            logger.exception(e)
            return False

        login_payload = {
            "username": self.loadboard_username,
            "password": self.loadboard_password,
            "submit.Signin": "Sign+in",
        }

        response_login = self.client.post(response_redirect.url, data=login_payload)

        response_code = self.client.post(response_login.next_request.url, data={"submit.Grant": "Grant"})

        authorization_code = httpx.QueryParams(response_code.next_request.url.params).get("code")

        return authorization_code

    def get_access_token(self):

        """Generate The Access Token or send the token from database if it did not expire"""

        # Check if the token is valid and update the header with it
        try:
            token = AccessToken.objects.get(loadboard_name=self.loadboard_name)
            if token.expires > round(time.time()) + self.token_max_time:
                self.client.headers.update({"Authorization": f"Bearer {token.access_token}"})
                return True
        except ObjectDoesNotExist as e:
            logger.exception(e)
            pass

        url = self.base_url + "/token"

        # Get the authotization Code
        authorization_code = self.get_authorization_code()

        if authorization_code is None:
            logger.info("Authorization Code is none.")
            return False

        client_credentials = self.loadboard_client_id + ":" + self.loadboard_client_secret
        encode_client_credentials = base64.b64encode(client_credentials.encode())
        decode_client_credentials = encode_client_credentials.decode()

        headers = {
            "Authorization": "Basic " + str(decode_client_credentials),
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Nauvus TMP Pro/1.47.2(nauvus@nauvus.com)",
        }

        payload = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "client_id": settings.LOADBOARD_CLIENT_ID,
            "redirect_uri": self.base_url + "/tokenreceiver",
        }

        # auth_response = requests.post(url=url, headers=header, data=body)
        auth_response = self.client.post(url, headers=headers, data=payload)
        auth_response = auth_response.json()

        access_token = auth_response.get("access_token")
        refresh_token = auth_response.get("refresh_token")
        expires = round(time.time()) + int(auth_response.get("expires_in"))

        data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires": expires,
        }

        # Update the header
        self.client.headers.update({"Authorization": f"Bearer {access_token}"})

        AccessToken.objects.update_or_create(loadboard_name=self.loadboard_name, defaults=data)

        return True

    class Decorators:
        @staticmethod
        def refresh_token(decorated):
            def wrapper(api, *arg, **kwargs):
                api.get_access_token()
                return decorated(api, *arg, **kwargs)

            return wrapper

    @staticmethod
    def get_body(states, next_token, max_age):
        """Payload Of Load Search API"""

        body = {
            "origin": {"type": "states", "states": [states]},
            "destination": {"type": "Anywhere"},
            "metadata": {
                "limit": 5000,
                "fields": "all",
                "type": "Regular",
                "nextToken": next_token,
                "sortBy": {"direction": "Descending", "field": "PostedDate"},
            },
            "maxAge": max_age,
            "includeLoadsWithoutLength": True,
            "includeLoadsWithoutWeight": True,
            "saveAsRecentSearch": False,
            "expandPosterInfo": True,
        }

        return body

    @Decorators.refresh_token
    def get_loads(self, max_age=None, us_states=[]):
        """Search the 123loadboard api for loads and import them.

        Params:
            max_age: the maximum age in days of the load
            us_states: an array of US state abbreviations to import e.g. ["GA", "AL"]
                If not included, it defaults to all states.

        Returns:
            _type_: _description_
        """

        loads = []

        states = us_states
        if len(us_states) == 0:
            # if no states are passed, then do all states
            states = US_STATES

        for state in states:
            if state not in US_STATES:
                # if not a US state, then skip this iteration
                logger.error(f"Could not import loads for {state}.  It is not a valid state in the USA.")
                continue
            is_last_result = False
            next_token = None
            while not is_last_result:
                search_url = self.base_url + "/loads/search"
                body = self.get_body(state, next_token, max_age)
                response = self.client.post(url=search_url, json=body)
                loads_data = response.json()

                try:
                    for load in loads_data.get("loads"):
                        loads.append(load)
                        is_last_result = loads_data.get("metadata").get("isLastResult")
                        next_token = loads_data.get("metadata").get("nextToken")
                except TypeError as e:
                    logger.exception(e)
                    break

        return loads

    @Decorators.refresh_token
    def get_load_details(self, load_id):

        url = f"{self.base_url}/loads/{load_id}"

        query = {"fields": "all", "onlineOnly": "true"}

        response = self.client.get(url=url, params=query)

        if response.status_code == 200 and response.content is not None:
            return response.json()

        logger.info(f"{response.status_code=}, {response.content=}")
        raise ObjectDoesNotExist(f"Could not find load {load_id} on Loadboard123.")

    @staticmethod
    def create_broker(load):
        """
        Create or update the Broker and returns the Broker object.

        load_id: Load uid from 123Loadboard

        mc_number: MC Number of the Broker from 123Loadboard
        """

        broker_details = load.get("poster")

        external_broker_id = broker_details.get("id")
        name = broker_details.get("name")

        try:
            mc_number = str(broker_details.get("docketNumber").get("number"))
        except AttributeError:
            mc_number = None

        broker = {
            "external_broker_id": external_broker_id,
            "name": name,
            "mc_number": mc_number,
            "metadata": "",
        }

        obj = None
        if mc_number:
            obj, broker_created = Broker.objects.get_or_create(mc_number=mc_number, defaults=broker)
            if broker_created:
                oatfi.save_broker(obj)
        else:
            # if no MC number for the broker, skip the load
            load_id = load.get("id")
            logger.info(f"Load {load_id} was not imported. MC Number for broker was not present")
            raise ValidationError("No MC number for broker")
            # obj, broker_created = Broker.objects.get_or_create(external_broker_id=external_broker_id, defaults=broker)

        return obj

    def process_loads(self, max_age=None, states=[]):

        """Process the Response Data"""
        logger.info(f"Importing loads from {states}")
        loads = self.get_loads(max_age, states)

        for load in loads:

            try:
                load_id = load.get("id")

                if load.get("status") != "Online":
                    # If the Load status is not Online, try to delete the load
                    self.delete_load(load_id)
                    continue

                broker = self.create_broker(load)

                # If the broker does not come from 123Loadboard, it goes on to the next load.
                if broker is None:
                    logger.info(f"Load {load_id} was not imported. Broker empty.")
                    continue

                self.save_update_load(load, broker)
            except Exception as e:
                logger.error(
                    f"Exception encountered when importing load {load_id} from 123Loadboard.  Full message: {repr(e)}"
                )

        return True

    def save_update_load(self, raw_load, broker):
        """Save or Update the Load"""
        load_id = raw_load.get("id")
        try:
            load = Load.objects.get(pk=load_id)
            if load.current_status != Load.Status.AVAILABLE:
                logger.info(f"Load {load_id} is no longer available; doing nothing.")
                return load
            # update the existing load if it is still available
            load = Loadboard123Load.normalize_load(raw_load, broker, load)
            logger.info(f"Load {load_id} is still available and will be updated.")
            load.save()
            return load
        except Load.DoesNotExist:
            pass

        load = Loadboard123Load.normalize_load(raw_load, broker)

        if not load:
            logger.info(f"Could not create load for load id {load_id}")
            return None
        # this should only execute for new loads that have not been seen before
        load_source_obj, load_source_created = LoadSource.objects.get_or_create(
            load_id=load_id,
            defaults={"source": self.loadboard_name, "load_id": load_id},
        )

        load.source = load_source_obj
        load.id = load_id
        load.save()
        logger.info(f"Load {load_id} was created.")
        return load

    def delete_load(self, load_id):

        """
        Delete the Load with status different of "Online" on 123Loadboard. Locally, the load with current_status
        different of "available" will NOT be deleted.
        """

        try:
            Load.objects.filter(source__load_id=load_id).filter(current_status="available").delete()
            LoadSource.objects.filter(load_id=load_id).delete()
            logger.info(f"Load {load_id} was removed.")
        except ObjectDoesNotExist:
            logger.info(f"Load {load_id} was not remove. It does not exist.")
            pass
