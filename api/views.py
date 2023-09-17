import logging
import traceback

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from api import forms, models, serializers
from api.permissions import IsAuthGoogleTask, IsPassedTurnstile
from basic_auth.constants import DAYS_USE_CREDITS_NO_ACCOUNT
from basic_auth.models import User
from email_finder.core.main import search_existing_or_find_emails
from services import email as email_service
from services import utils
from services.captcha import verify_captcha_response
from services.mixpanel import EventName, track_event
from services.zerobounce import zerobouncesdk

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsPassedTurnstile])
def find_emails(request):
    form = forms.FindEmailForm(request.data)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        user = models.AnonUser.objects.filter(id=cleaned_data["visitor_id"]).first()
        if not user:
            user = models.AnonUser.objects.create(
                id=cleaned_data["visitor_id"],
                user_agent=request.META.get("HTTP_USER_AGENT"),
            )
        elif (
            not user.has_searches_credits()
            and (utils.get_utc_now() - user.restore_searches_at).days
            >= DAYS_USE_CREDITS_NO_ACCOUNT
        ):
            user.restore_number_searches()

        if not user.has_searches_credits():
            return Response(status=status.HTTP_403_FORBIDDEN)

        logger.info(f"Finding emails for user {user}")

        try:
            first = cleaned_data["first_name"]
            middle = cleaned_data["middle_name"]
            last = cleaned_data["last_name"]
            domain = cleaned_data["domain_name"]
            search_result, exists = search_existing_or_find_emails(first, middle, last, domain)

            result_data = {
                "first_name": first,
                "last_name": last,
                "link": domain,
            }
            if exists:
                result_data["result_on_db"] = search_result
            else:
                (
                    zb_emails,
                    breach_emails,
                    social_emails,
                ) = search_result.get_found_emails_in_steps()
                result_data["zerobounce_api"] = "\n".join(zb_emails)
                result_data["is_pwned"] = "\n".join(breach_emails)
                result_data["social"] = "\n".join(social_emails)
                (
                    result_data["additional_emails"],
                    result_data["google_search"],
                ) = search_result.get_google_search_data()
            models.Search.objects.create(**result_data)

            response_data = search_result.result
            utils.remove_opt_out_emails(response_data)
        except Exception as e:
            logger.error(f"Error when finding emails: {e}")
            traceback.print_exc()
            return Response(
                {"message": "Error occured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        user.number_searches += 1
        user.save()
        response_data.update({"number_searches": user.number_searches})

        track_event(
            user.id,
            EventName.free_search,
            {
                "first_name": first,
                "last_name": last,
                "domain_name": domain,
            },
        )
        return Response(response_data)
    else:
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def contact_us(request):
    if "captcha" not in request.data or not verify_captcha_response(request.data["captcha"]):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    serializer = serializers.ContactSerializer(data=request.data)
    if serializer.is_valid():
        contact = serializer.save()
        data = serializer.data
        email_service.send_email(
            data["email"],
            "Thank you for contacting us",
            email_service.CONTACT_US_EMAIL.format(first_name=contact.get_first_name()),
        )
        email_service.send_email(
            email_service.AUTOMATIC_EMAIL[0],
            f"New message from {data['email']}",
            contact.get_full_message(),
            reply_to=data["email"],
        )
        return Response({"message": "Thanks! we will respond within the next 24-hours"})
    return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def payment_webhook(request):
    print("payment_webhook", request, request.body)
    return Response("ok")


class OptOutView(CreateAPIView):
    serializer_class = serializers.OptOutSerializer
    permission_classes = (IsPassedTurnstile,)


@api_view(["POST"])
@permission_classes([IsPassedTurnstile])
def email_verifier(request):
    form = forms.EmailVerifierForm(request.data)
    if not form.is_valid():
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)
    cleaned_data = form.cleaned_data
    user = models.AnonUser.objects.filter(id=cleaned_data["visitor_id"]).first()
    if not user:
        user = models.AnonUser.objects.create(
            id=cleaned_data["visitor_id"],
            user_agent=request.META.get("HTTP_USER_AGENT"),
        )
    elif (
        not user.has_verifier_credits()
        and (utils.get_utc_now() - user.restore_verifiers_at).days >= DAYS_USE_CREDITS_NO_ACCOUNT
    ):
        user.restore_number_verifiers()
    if not user.has_verifier_credits():
        return Response(status=status.HTTP_403_FORBIDDEN)
    user.number_verifiers += 1
    user.save()
    r = zerobouncesdk.validate(email=cleaned_data["email"])
    return Response({"status": r.status.name, "sub_status": r.sub_status.name})


@api_view(["POST"])
@permission_classes([IsAuthGoogleTask])
def send_following_email_afer_sign_up(request):
    user = User.objects.filter(id=request.data.get("user_id")).first()
    if user:
        email_service.send_email(
            user.email,
            "Thanks for signing up with Emailchaser",
            email_service.FOLLOWING_AFER_SIGN_UP_EMAIL.format(first_name=user.first_name),
            from_email=email_service.GEORGE_GETEMAILCHASER_EMAIL,
        )
    return Response()
