import os.path
import time

import cryptography
from cryptography.hazmat.primitives import serialization as crypto_serialization
from django.conf import settings
from jose import jws, jwt


def docusign_token():
    iat = time.time()
    exp = iat + (3600 * 24 * 365)
    payload = {
        "sub": settings.DOCUSIGN_CLIENT_USER_ID,
        "iss": settings.DOCUSIGN_CLIENT_AUTH_ID,
        "iat": iat,
        "exp": exp,
        "aud": "account-d.docusign.com",
        "scope": "signature impersonation",
    }
    header = {
        "alg": "RS256",
        "typ": "JWT"
    }

    private_file = os.path.dirname(__file__)
    try:
        with open(f"{private_file}/private_key.pem", "rb") as key_file:
            private_key = crypto_serialization.load_pem_private_key(key_file.read(), password=None)
    except FileNotFoundError:
        return None

    key = private_key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption(),
    )

    jwt_token = jws.sign(payload, key, algorithm="RS256")
    return jwt_token
