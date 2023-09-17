import os

import django.contrib.auth.models as dauth_models
from dateutil.relativedelta import relativedelta
from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils import timezone

from basic_auth.constants import USER_TRIAL_HOURS
from services import email as email_service
from services import mailchimp, utils
from services.mixpanel import track_signup


class Plan(models.Model):
    TRIAL, ANNUAL_NORMAL, ANNUAL_ENTERPRISE = (
        "TRIAL",
        "ANNUAL_NORMAL",
        "ANNUAL_ENTERPRISE",
    )
    TYPE_CHOICES = [
        (TRIAL, "Trial"),
        (ANNUAL_NORMAL, "Full Annual Account (Normal)"),
        (ANNUAL_ENTERPRISE, "Full Annual Account (Enterprise)"),
    ]
    plan_type = models.TextField(choices=TYPE_CHOICES)
    price = models.FloatField()
    search_credits = models.IntegerField()
    verify_credits = models.IntegerField(default=0)

    class Meta:
        db_table = "plan"

    def __str__(self) -> str:
        return self.plan_type

    def get_days(self):
        if self.plan_type == self.TRIAL:
            return 7
        else:
            return 365


class CustomUserManager(dauth_models.UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(dauth_models.AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    delete_reason = models.TextField(blank=True)
    avatar = models.FileField(default=None, null=True, upload_to="avatar")
    google_auth = models.BooleanField(default=False)
    token = models.CharField(max_length=265, default=None, null=True)
    is_verified = models.BooleanField(default=False)
    unverified_changed_email = models.CharField(max_length=265, default=None, null=True)
    completed_tasks = models.JSONField(default=list)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        indexes = [models.Index(fields=["unverified_changed_email"])]
        db_table = "user"

    @property
    def plan_data(self):
        if not hasattr(self, "_plan_data"):
            setattr(self, "_plan_data", self.get_plan_data())
        return self._plan_data

    def get_plan_data(self):
        return UserPlan.objects.filter(user=self).order_by("-created_at").first()

    @property
    def search_credits(self):
        if self.plan_data:
            return self.plan_data.search_credits
        return 0

    @property
    def verify_credits(self):
        if self.plan_data:
            return self.plan_data.verify_credits
        return 0

    def has_search_credits(self, number_credits=1):
        return self.search_credits >= number_credits

    def use_search_credits(self, number_credits=1):
        self.plan_data.search_credits -= number_credits
        self.plan_data.save()

    def has_verify_credits(self, number_credits=1):
        return self.verify_credits >= number_credits

    def use_verify_credits(self, number_credits=1):
        self.plan_data.verify_credits -= number_credits
        self.plan_data.save()

    def clear_credits(self):
        self.plan_data.status = UserPlan.EXPIRED
        self.plan_data.search_credits = 0
        self.plan_data.save()

    def generate_token(self):
        self.token = utils.get_token()
        self.save()

    def send_email_verification_url(self):
        self.generate_token()
        url = f"{os.getenv('FRONTEND_URL')}/verify-email/{self.token}"
        email_service.send_email(
            self.email,
            "Please confirm your account",
            email_service.SIGNUP_CONFIRM_EMAIL.format(first_name=self.first_name, url=url),
        )

    def verify_user(self):
        self.is_verified = True
        self.save()

    def send_forgot_password_url(self):
        self.generate_token()
        url = f"{os.getenv('FRONTEND_URL')}/reset-password/{self.token}"
        email_service.send_email(
            self.email,
            "Your Emailchaser password reset request",
            email_service.FORGOT_PASSWORD_EMAIL.format(first_name=self.first_name, url=url),
        )

    def change_password(self, password):
        self.set_password(password)
        self.save()
        email_service.send_email(
            self.email,
            "Your Emailchaser account password has changed",
            email_service.CHANGED_PASSWORD_SUCCESS_EMAIL.format(
                first_name=self.first_name, email=self.email
            ),
        )

    def send_email_for_changing(self):
        self.generate_token()
        url = f"{os.getenv('FRONTEND_URL')}/change-email/{self.token}"
        email_service.send_email(
            self.unverified_changed_email,
            "Change your email",
            email_service.CHANGE_EMAIL.format(first_name=self.first_name, url=url),
        )

    def check_verify_status(self):
        return self.is_verified or timezone.now() < self.date_joined + relativedelta(
            hours=USER_TRIAL_HOURS
        )


class UserPlan(models.Model):
    ACTIVE, EXPIRED, PENDING = (
        "ACTIVE",
        "EXPIRED",
        "PENDING",
    )
    STATUS_CHOICES = [
        (ACTIVE, "Plan is active"),
        (EXPIRED, "Plan is expired"),
        (PENDING, "Waiting for payment"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_plans")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    status = models.TextField(choices=STATUS_CHOICES)
    search_credits = models.IntegerField(default=0)
    verify_credits = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["status"])]
        db_table = "user_plan"


def create_user(plan_type, email, password=None, **kwargs):
    plan = Plan.objects.filter(plan_type=plan_type).first()
    user = User.objects.create_user(email, password, **kwargs)
    UserPlan.objects.create(
        user=user,
        plan=plan,
        status=UserPlan.ACTIVE,
        search_credits=plan.search_credits,
        verify_credits=plan.verify_credits,
    )
    track_signup(user, plan)
    if plan_type == Plan.ANNUAL_NORMAL:
        mailchimp.subscribe(
            {
                "email_address": email,
                "status": "subscribed",
                "merge_fields": {
                    "FNAME": kwargs.get("first_name"),
                    "LNAME": kwargs.get("last_name"),
                },
            }
        )
    return user
