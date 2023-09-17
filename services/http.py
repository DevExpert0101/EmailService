import json
import traceback

import requests


def get_json(url, data):
    try:
        r = requests.post(url, data=data, timeout=5)
        return json.loads(r.content)
    except Exception as e:
        print(f"Error when get json {url} {data}", e)
        traceback.print_exc()
