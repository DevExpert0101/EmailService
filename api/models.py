from django.db import models
from django.utils.html import format_html
from django.utils.timezone import now

from basic_auth import constants
from email_finder.core.constants import (
    BREACH_SEARCH_TYPE,
    SOCIAL_SEARCH_TYPE,
    ZEROBOUNCE_SEARCH_TYPE,
)
from services import utils


class AnonUser(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    user_agent = models.TextField(null=True, blank=True)
    ip = models.TextField(null=True, blank=True)
    number_searches = models.PositiveIntegerField(default=0)
    number_verifiers = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    restore_searches_at = models.DateTimeField(default=now)
    restore_verifiers_at = models.DateTimeField(default=now)

    class Meta:
        db_table = "anon_user"

    def __str__(self):
        return f"{self.id} - {self.user_agent}"

    def has_searches_credits(self):
        return self.number_searches < constants.DEFAULT_SEARCH_CREDITS_NO_ACCOUNT

    def has_verifier_credits(self):
        return self.number_verifiers < constants.DEFAULT_SEARCH_CREDITS_NO_ACCOUNT

    def restore_number_searches(self):
        self.number_searches = 0
        self.restore_searches_at = utils.get_utc_now()
        self.save()

    def restore_number_verifiers(self):
        self.number_verifiers = 0
        self.restore_verifiers_at = utils.get_utc_now()
        self.save()


class Contact(models.Model):
    full_name = models.CharField(max_length=256)
    job_title = models.CharField(max_length=256)
    email = models.CharField(max_length=256)
    phone = models.CharField(max_length=256, null=True, blank=True)
    message = models.TextField()

    class Meta:
        db_table = "contact"

    def get_full_message(self):
        return (
            f"Full name: {self.full_name}\n"
            f"Business email: {self.email}\n"
            f"Phone number: {self.phone}\n"
            f"Job title: {self.job_title}\n\n{self.message}"
        ).replace("\n", "<br />")

    def get_first_name(self):
        return self.full_name.split()[0]


class SearchResult(models.Model):
    first_name = models.CharField(max_length=256)
    middle_name = models.CharField(null=True, max_length=256, blank=True)
    last_name = models.CharField(max_length=256)
    domain_name = models.CharField(max_length=256)
    result = models.JSONField(max_length=256)
    from_bulk_search = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["first_name", "middle_name", "last_name", "domain_name"]),
            models.Index(fields=["first_name", "last_name", "domain_name"]),
        ]
        db_table = "search_result"

    def get_found_emails_in_steps(self):
        zb_emails = []
        breach_emails = []
        social_emails = []
        for e, data in self.result.get("emails", {}).items():
            if type(data) == dict:
                data = [data]
            for found_data in data:
                found_in_step = found_data["type"]
                if found_in_step == ZEROBOUNCE_SEARCH_TYPE:
                    zb_emails.append(e)
                elif found_in_step == BREACH_SEARCH_TYPE:
                    breach_emails.append(e)
                elif found_in_step == SOCIAL_SEARCH_TYPE:
                    social_emails.append(e)
        return zb_emails, breach_emails, social_emails

    def get_google_search_data(self):
        (
            zb_emails,
            breach_emails,
            social_emails,
        ) = self.get_found_emails_in_steps()

        google_search_results = self.result.get("google_searches", {})
        additional_emails = len(
            set(google_search_results) - set(zb_emails + breach_emails + social_emails)
        )
        google_search = sum([len(pages) for pages in google_search_results.values()])
        return additional_emails, google_search


class Search(models.Model):
    first_name = models.TextField(null=True)
    last_name = models.TextField(null=True)
    link = models.TextField(null=True)
    result_on_db = models.ForeignKey(SearchResult, null=True, on_delete=models.SET_NULL)
    is_pwned = models.TextField(null=True)
    social = models.TextField(null=True)
    email_scraper = models.TextField(null=True)
    zerobounce_api = models.TextField(null=True)
    google_search = models.IntegerField(null=True)
    additional_emails = models.IntegerField(null=True)
    date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Searches"
        db_table = "search"

    def found_result(self):
        if not self.result_on_db:
            return ""
        return format_html(
            '<a target="_blank" href="/admin/api/searchresult/{}/change/">Yes</a>'.format(
                self.result_on_db.id
            )
        )


class EmailFinderHistory(models.Model):
    ZERO_BOUNCE_STEP, CHECK_PWN_STEP, CHECK_SOCIAL_STEP, GOOGLE_SEARCH_STEP = (
        "ZERO_BOUNCE",
        "CHECK_PWN",
        "CHECK_SOCIAL",
        "GOOGLE_SEARCH",
    )
    STEP_CHOICES = [
        (ZERO_BOUNCE_STEP, "Check valid using zerobounce api"),
        (CHECK_PWN_STEP, "Check if emails are pwned"),
        (CHECK_SOCIAL_STEP, "Check emails on twitter, microsoft,.."),
        (GOOGLE_SEARCH_STEP, "Search emails using google search api"),
    ]
    search_result = models.ForeignKey(
        SearchResult, on_delete=models.CASCADE, default=None, null=True, blank=True
    )
    step = models.CharField(choices=STEP_CHOICES, max_length=20)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "email_finder_history"


class OptOutRequest(models.Model):
    full_name = models.TextField()
    email = models.EmailField(max_length=100, db_index=True)

    class Meta:
        db_table = "opt_out_request"
