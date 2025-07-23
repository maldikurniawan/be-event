import requests
from decouple import config


def verify_turnstile_token(token, remoteip=None):
    """Verifikasi token ke Cloudflare"""

    data = {
        "secret": config("TURNSTILE_SECRET_KEY"),
        "response": token,
    }
    if remoteip:
        data["remoteip"] = remoteip

    r = requests.post(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify", data=data
    )
    result = r.json()
    return result.get("success", False)
