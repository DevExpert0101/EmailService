import logging
import traceback

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from api.permissions import IsAuthGoogleTask
from basic_auth.models import User
from email_finder.core.main import search_existing_or_find_emails
from email_finder.models import BulkEmailFinderRecord, LinkedinEmailFinderRecord
from email_verifier.models import BulkEmailVerifierRecord
from services import email as email_service
from services.zerobounce import zb_verify_email

logger = logging.getLogger(__name__)


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


@api_view(["POST"])
@permission_classes([IsAuthGoogleTask])
def process_email_finder_bulk_records(request):
    from_linkedin = request.data.get("from_linkedin")
    RecordClass = LinkedinEmailFinderRecord if from_linkedin else BulkEmailFinderRecord
    bulk = None
    for record_id in request.data.get("records", []):
        bulk_record = RecordClass.objects.filter(id=record_id).first()
        if not bulk_record or not bulk_record.in_queue:
            continue

        bulk = bulk_record.bulk
        user = bulk.user
        if not user.has_search_credits():
            bulk_record.status = RecordClass.STATUS_LOW_CREDIT
            bulk_record.save()
            continue

        try:
            search_result, _ = search_existing_or_find_emails(
                bulk_record.first_name,
                bulk_record.middle_name,
                bulk_record.last_name,
                bulk_record.domain_name,
                is_bulk=True,
            )
            bulk_record.search_result = search_result
            user.use_search_credits()
            if bulk_record.has_found_emails():
                bulk_record.status = RecordClass.STATUS_FOUND
            else:
                bulk_record.status = RecordClass.STATUS_NOT_FOUND
        except Exception as e:
            logger.error(f"Error when process record of bulk email finder: {e}")
            traceback.print_exc()
            bulk_record.status = RecordClass.STATUS_SERVER_ERROR
        bulk_record.save()

    if bulk and bulk.is_completed:
        if from_linkedin:
            subject = f"LinkedIn Email Finder export ({bulk.name}) is complete"
            email_content = email_service.DONE_LINKEDIN_EMAIL_FINDER_EMAIL
        else:
            subject = f"Bulk Email Finder search ({bulk.name}) is complete"
            email_content = email_service.DONE_BULK_EMAIL_FINDER_EMAIL
        email_service.send_email(
            user.email,
            subject,
            email_content.format(first_name=user.first_name, bulk_name=bulk.name),
            from_email=email_service.NOTIFICATION_EMAIL,
        )
    return Response()


@api_view(["POST"])
@permission_classes([IsAuthGoogleTask])
def process_email_verifier_bulk_records(request):
    bulk = None
    for record_id in request.data.get("records", []):
        bulk_record = BulkEmailVerifierRecord.objects.filter(id=record_id).first()
        if not bulk_record or not bulk_record.in_queue:
            continue

        bulk = bulk_record.bulk
        user = bulk.user
        if not user.has_verify_credits():
            bulk_record.status = BulkEmailVerifierRecord.STATUS_LOW_CREDIT
            bulk_record.save()
            continue

        _status, sub_status = zb_verify_email(bulk_record.email)
        bulk_record.status = _status
        bulk_record.sub_status = sub_status
        if _status:
            bulk_record.task_status = BulkEmailVerifierRecord.STATUS_DONE
        else:
            bulk_record.task_status = BulkEmailVerifierRecord.STATUS_SERVER_ERROR
        bulk_record.save()

    if bulk and bulk.is_completed:
        email_service.send_email(
            user.email,
            f"Bulk Email Verifier search ({bulk.name}) is complete",
            email_service.DONE_BULK_EMAIL_VERIFIER_EMAIL.format(
                first_name=user.first_name, bulk_name=bulk.name
            ),
            from_email=email_service.NOTIFICATION_EMAIL,
        )
    return Response()
