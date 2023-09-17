import os

import fingerprint_pro_server_api_sdk
from fingerprint_pro_server_api_sdk.rest import ApiException

configuration = fingerprint_pro_server_api_sdk.Configuration(
    api_key=os.getenv("FINGERPRINT_SECRET_KEY")
)

fingerprint_api = fingerprint_pro_server_api_sdk.FingerprintApi(configuration)


def validate_visitor(visitor_id, request_id):
    try:
        api_response = fingerprint_api.get_visits(visitor_id, request_id=request_id)
        if api_response.visits:
            return True
    except ApiException as e:
        print("Exception when calling DefaultApi->visitors_visitor_id_get: %s\n" % e)
    return False
