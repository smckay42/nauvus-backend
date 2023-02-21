import base64
import uuid

import pymongo
import requests
import httpx
from django.conf import settings
from urllib.parse import parse_qs


# client = pymongo.MongoClient(settings.MONGODB_HOST)
# db = client[settings.MONOGO_DB_NAME]
# mongo_collection = db["loads_accesstoken"]


def get_authorization_code():
    state = str(uuid.uuid4())

    # s = requests.session()

    timeout = httpx.Timeout(10.0, connect=20.0)
    client = httpx.Client(timeout=timeout, verify=False)

    url = "https://api.dev.123loadboard.com/authorize"
    headers = {"User-Agent": "Nauvus TMP Pro/1.47.2(nauvus@nauvus.com)"}

    # s.headers.update(headers)

    query = {
        "response_type": "code",
        "client_id": settings.LOADBOARD_CLIENT_ID,
        "redirect_uri": "https://api.dev.123loadboard.com/tokenreceiver",
        "scope": "offline_access",
        "state": state,
        "login_hint": settings.LOADBOARD_USERNAME
    }

    try:
        response_redirect = client.get(url, params=query, headers=headers, follow_redirects=True)
    except httpx.ConnectTimeout:
        return None

    # response_redirect = s.get(url, params=query, allow_redirects=True)

    login_payload = {'username': settings.LOADBOARD_USERNAME, 'password': settings.LOADBOARD_PASSWORD,
                     'submit.Signin': 'Sign+in'}

    response_login = client.post(response_redirect.url, data=login_payload)
    # response_login = s.post(response_redirect.url, data=login_payload)

    response_code = client.post(response_login.next_request.url, data={"submit.Grant": "Grant"})
    # response_code = s.post(response_login.url, data={"submit.Grant": "Grant"})

    authorization_code = httpx.QueryParams(response_code.next_request.url.params).get('code')
    # authorization_code = parse_qs(response_code.url).get('code')

    return authorization_code


def get_access_token():
    """Generate The Access Token and Refresh Token"""

    timeout = httpx.Timeout(10.0, connect=60.0)
    client = httpx.Client(timeout=timeout)

    url = "https://api.dev.123loadboard.com/token"

    authorization_code = get_authorization_code()

    if authorization_code is None:
        return None

    client_credentials = (
        settings.LOADBOARD_CLIENT_ID + ":" + settings.LOADBOARD_CLIENT_SECRET
    )
    encode_client_credentials = base64.b64encode(client_credentials.encode())
    decode_client_credentials = encode_client_credentials.decode()

    # header = {"Authorization": "Basic " + str(decode_client), "User-Agent": "Nauvus TMP Pro/1.47.2(nauvus@nauvus.com)"}

    headers = {
        "Authorization": "Basic " + str(decode_client_credentials),
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Nauvus TMP Pro/1.47.2(nauvus@nauvus.com)"
    }

    payload = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "client_id": settings.LOADBOARD_CLIENT_ID,
        "redirect_uri": "https://api.dev.123loadboard.com/tokenreceiver"
    }

    # auth_response = requests.post(url=url, headers=header, data=body)
    auth_response = client.post(url, headers=headers, data=payload)
    auth_response = auth_response.json()

    access_token = auth_response.get("access_token")
    refresh_token = auth_response.get("refresh_token")

    data = {"access_token": access_token, "refresh_token": refresh_token}
    # mongo_collection.remove({})
    # mongo_collection.insert_one(data)

    return access_token


def get_access_token_by_refresh_token():
    "Create Access Token With Refresh Token"

    url = "https://api.dev.123loadboard.com/token"

    client = (
        settings.LOADBOARD_CLIENT_ID + ":" + settings.LOADBOARD_CLIENT_SECRET
    )
    encode_client = base64.b64encode(client.encode())
    decode_client = encode_client.decode()

    header = {"Authorization": "Basic " + str(decode_client)}

    # query = mongo_collection.find_one({})
    # refresh_token = query.get("refresh_token")
    #
    # body = {
    #     "grant_type": "refresh_token",
    #     "refresh_token": refresh_token,
    # }

    auth_response = requests.post(url=url, headers=header, json=body)
    access_token = auth_response.json().get("access_token")
    new_refresh_token = auth_response.json().get("refresh_token")

    # mongo_collection.remove({})
    # mongo_collection.insert_one(
    #     {
    #         "access_token": access_token,
    #         "refresh_token": new_refresh_token,
    #     }
    # )
