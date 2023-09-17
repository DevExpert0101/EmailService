import logging
import os

from django.conf import settings
from mixpanel import Mixpanel

logger = logging.getLogger(__name__)


class EventName:
    free_search = "Free email search from homepage (not logged in)"
    user_search = "Paid email search from inside account (logged in)"
    signup_trial = "7-day trial signup"
    signup_annual = "Startup annual account signup"
    free_lead_search = "Free lead search from homepage (not logged in)"
    paid_lead_search = "Paid lead search from inside account (logged in)"


mixpanel = Mixpanel(os.getenv("MIXPANEL_PROJECT_TOKEN"))


def track_signup(user, plan):
    if settings.DEBUG:
        return
    from basic_auth.models import Plan

    if plan.plan_type == Plan.TRIAL:
        event_name = EventName.signup_trial
    else:
        event_name = EventName.signup_annual
    try:
        mixpanel.people_set(
            user.email,
            {
                "$first_name": user.first_name,
                "$last_name": user.last_name,
                "$email": user.email,
            },
            meta={"$ignore_time": True, "$ip": 0},
        )
        mixpanel.track(user.email, event_name)
    except Exception as e:
        logger.error(f"Error when tracking sign up: {str(e)}")


def track_event(user_id, event_name, data={}):
    if settings.DEBUG:
        return
    try:
        mixpanel.track(user_id, event_name, data)
    except Exception as e:
        logger.error(f"Error when tracking {event_name}: {str(e)}")
