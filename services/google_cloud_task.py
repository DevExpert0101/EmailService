import json
import logging
import os

from google.cloud import tasks_v2
from google.protobuf import duration_pb2, timestamp_pb2

from services.utils import get_utc_time_from_now

logger = logging.getLogger(__name__)

client = tasks_v2.CloudTasksClient()

PROJECT = os.getenv("GOOGLE_PROJECT_ID")
QUEUE = os.getenv("GOOGLE_QUEUE")
LOCATION = os.getenv("GOOGLE_LOCATION")
BASE_TASK_URL = os.getenv("GOOGLE_TASK_HANDLER_URL")
GOOGLE_TASK_SECRET = os.getenv("GOOGLE_TASK_SECRET")

parent = client.queue_path(PROJECT, LOCATION, QUEUE)


def create_google_task(url, payload, in_seconds=None, deadline=900):
    payload["secret"] = GOOGLE_TASK_SECRET
    task = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": url,
            "headers": {"Content-type": "application/json"},
            "body": json.dumps(payload).encode(),
        }
    }

    # Create Timestamp protobuf.
    if in_seconds:
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(get_utc_time_from_now(seconds=in_seconds))
        task["schedule_time"] = timestamp

    duration = duration_pb2.Duration()
    duration.FromSeconds(deadline)
    task["dispatch_deadline"] = duration

    # Use the client to build and send the task.
    response = client.create_task(request={"parent": parent, "task": task})

    logging.info(f"Created task {response.name}")
