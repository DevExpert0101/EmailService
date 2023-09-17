import logging
import os

from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError

logger = logging.getLogger(__name__)

mailchimp_client = Client()
mailchimp_client.set_config(
    {"api_key": os.getenv("MAILCHIMP_API_KEY"), "server": os.getenv("MAILCHIMP_SERVER")}
)


def subscribe(data):
    try:
        mailchimp_client.lists.add_list_member(os.getenv("MAILCHIMP_EMAIL_LIST_ID"), data)
    except ApiClientError as error:
        logger.error(f"Error when subscribe mailchimp: {str(error)}")
