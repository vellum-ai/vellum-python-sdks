import hashlib
import hmac
import os
import time

from requests import PreparedRequest


def _sign_request(request: PreparedRequest, secret: str) -> None:
    """
    Sign a request with HMAC using the same pattern as Django implementation.

    Args:
        request: The prepared request to sign
        secret: The HMAC secret string
    """
    timestamp = str(int(time.time()))

    body = request.body or b""
    if isinstance(body, str):
        body = body.encode()

    message = f"{timestamp}\n{request.method}\n{request.url}\n".encode() + body

    signature = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()

    hmac_headers = {
        "X-Vellum-Timestamp": timestamp,
        "X-Vellum-Signature": signature,
    }

    request.headers.update(hmac_headers)


def sign_request_with_env_secret(request: PreparedRequest) -> None:
    """
    Sign a request using VELLUM_HMAC_SECRET environment variable if available.

    Args:
        request: The prepared request to sign
    """
    hmac_secret = os.environ.get("VELLUM_HMAC_SECRET")
    if hmac_secret:
        _sign_request(request, hmac_secret)
