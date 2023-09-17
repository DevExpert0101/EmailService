import logging
import os

from zerobouncesdk import zerobouncesdk

zerobouncesdk.initialize(os.getenv("ZEROBOUNCE_API_KEY"))

logger = logging.getLogger(__name__)


class ZbStatus:
    valid = "valid"
    invalid = "invalid"
    catch_all = "catch-all"


def zb_verify_email(email):
    status, sub_status = None, None
    try:
        r = zerobouncesdk.validate(email=email)
        status = r.status.name
        sub_status = r.sub_status.name
    except Exception as e:
        logger.error(f"Error whening verifying email {email}: {str(e)}")
    return status, sub_status
