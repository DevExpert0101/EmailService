import os

from .http import get_json


def verify_captcha_response(captcha_response):
    r = get_json(
        "https://www.google.com/recaptcha/api/siteverify",
        {"secret": os.getenv("CAPTCHA_SECRET_KEY"), "response": captcha_response},
    )
    return r and r.get("success")
