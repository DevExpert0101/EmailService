from django.urls import path
from django.urls.conf import include

from api import views, views_tasks

urlpatterns = [
    path("find-emails/", views.find_emails, name="find_emails"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("opt-out/", views.OptOutView.as_view(), name="opt_out"),
    path("email-verifier/", views.email_verifier, name="email_verifier"),
    path(
        "tasks/",
        include(
            [
                path(
                    "send-following-email-afer-sign-up/",
                    views_tasks.send_following_email_afer_sign_up,
                    name="send_following_email_afer_sign_up",
                ),
                path(
                    "process_email_finder_bulk_records/",
                    views_tasks.process_email_finder_bulk_records,
                    name="process_email_finder_bulk_records",
                ),
                path(
                    "process_email_verifier_bulk_records/",
                    views_tasks.process_email_verifier_bulk_records,
                    name="process_email_verifier_bulk_records",
                ),
            ]
        ),
    ),
]
