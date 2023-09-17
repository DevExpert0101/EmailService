import os

from .http import get_json


def verify_turnstile_token(token):
    r = get_json(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify",
        {"secret": os.getenv("CLOUDFLARE_TURNSTILE_SECRET_KEY"), "response": token},
    )
    return r and r.get("success")
