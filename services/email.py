import logging
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)

SUPPORT_EMAIL = "support@emailchaser.com"
AUTOMATIC_EMAIL = ("support@getemailchaser.com", "Emailchaser")
NOTIFICATION_EMAIL = ("notifications@getemailchaser.com", "Emailchaser")
GEORGE_GETEMAILCHASER_EMAIL = ("george@getemailchaser.com", "George Wauchope")

CONTACT_US_EMAIL = (
    "Hi {first_name},<br /><br />"
    "Thank you for contacting us.<br /><br />"
    "We have received your email, and will respond within the next 24-hours.<br /><br />"
    "If you don’t see a response from us, then please check your junk/spam folder.<br /><br />"
    f"If you still don’t see a response, then you can email us directly at {SUPPORT_EMAIL}"
    "<br /><br />Regards,<br />"
    "The Emailchaser Team"
)

SIGNUP_CONFIRM_EMAIL = (
    "Hi {first_name},<br /><br />"
    "Please confirm your account.<br /><br />"
    '<a href="{url}">Confirm Your Email</a><br /><br />'
    "Or, copy and paste the following URL into your browser:<br />{url}<br /><br />"
    "Regards,<br />"
    "The Emailchaser Team"
)

FORGOT_PASSWORD_EMAIL = (
    "Hi {first_name},<br /><br />"
    "A request has been received to change the password for your Emailchaser account.<br /><br />"
    '<a href="{url}">Reset password</a><br /><br />'
    f"If you did not initiate this request, please contact us immediately at {SUPPORT_EMAIL}"
    "<br /><br />Regards,<br />"
    "The Emailchaser Team"
)

CHANGED_PASSWORD_SUCCESS_EMAIL = (
    "Hi {first_name},<br /><br />"
    "We’re confirming that you changed your Emailchaser account password for {email}<br /><br />"
    f"If you did not initiate this request, please contact us immediately at {SUPPORT_EMAIL}"
    "<br /><br />Regards,<br />"
    "The Emailchaser Team"
)

CHANGE_EMAIL = (
    "Hi {first_name},<br /><br />"
    "A request has been received to use your email for the Emailchaser account.<br /><br />"
    '<a href="{url}">Change email</a><br /><br />'
    "If you did not initiate this request, just ignore this email.<br /><br />"
    "Regards,<br />"
    "The Emailchaser Team"
)

DELETE_NOTIFICATION_FOR_ADMIN_EMAIL = (
    "Hi Admin,<br /><br />"
    "First name: {first_name}.<br /><br />"
    "Last name: {last_name}.<br /><br />"
    "Email address: ${email}<br /><br />"
    "Delete reason: ${delete_reason}."
)

FOLLOWING_AFER_SIGN_UP_EMAIL = (
    "Hi {first_name},<br /><br />"
    "I'm the founder of Emailchaser and just wanted to personally "
    "thank you for trying our tool.<br /><br />"
    "Let me know if you have any questions or need help. "
    "I'm also available to do a 1 on 1 onboarding call if needed.<br /><br />"
    "Thanks,<br />George<br /><br /><br />"
    "George Wauchope | Founder<br />Emailchaser<br />Grand Cayman, Cayman Islands<br />"
    '<a href="mailto:george@emailchaser.com" target="_blank">george@emailchaser.com</a> | '
    '<a href="https://www.emailchaser.com" target="_blank">emailchaser.com</a>'
)

DONE_BULK_EMAIL_FINDER_EMAIL = (
    "Hi {first_name},<br /><br />"
    "Your Bulk Email Finder search ({bulk_name}) is complete.<br /><br />"
    "Log into your Emailchaser account to view the results."
)

DONE_LINKEDIN_EMAIL_FINDER_EMAIL = (
    "Hi {first_name},<br /><br />"
    "Your Linkedin Email Finder export ({bulk_name}) is complete.<br /><br />"
    "Log into your Emailchaser account to view the results."
)

DONE_BULK_EMAIL_VERIFIER_EMAIL = (
    "Hi {first_name},<br /><br />"
    "Your Bulk Email Verifier search ({bulk_name}) is complete.<br /><br />"
    "Log into your Emailchaser account to view the results."
)


def send_email(to_email, subject, html_content, reply_to=None, from_email=AUTOMATIC_EMAIL):
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )
    if reply_to:
        message.reply_to = reply_to
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)
    except Exception as e:
        logger.error(f"Error when sending email from {from_email} to {to_email}: {str(e)}")
