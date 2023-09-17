import binascii
import datetime as dt
import os

import pytz


def get_token():
    return binascii.hexlify(os.urandom(20)).decode()


def get_utc_now():
    return dt.datetime.now(pytz.utc)


def get_utc_time_from_now(**kwargs):
    return dt.datetime.utcnow() + dt.timedelta(**kwargs)


def remove_opt_out_emails(result):
    from api.models import OptOutRequest

    emails = {}
    for e, data in result.get("emails", {}).items():
        if not OptOutRequest.objects.filter(email=e).exists():
            emails[e] = data
    result["emails"] = emails


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]
