from django import forms
from django.core import validators
from django.core.exceptions import ValidationError

from basic_auth.constants import PERSONAL_EMAIL_DOMAINS
from basic_auth.models import Plan
from services import captcha
from services.fingerprint import validate_visitor


def plan_type_validator(plan_type):
    if plan_type not in [Plan.TRIAL, Plan.ANNUAL_NORMAL, Plan.ANNUAL_ENTERPRISE]:
        raise ValidationError("Plan is not supported")


def captcha_validator(captcha_response):
    if not captcha.verify_captcha_response(captcha_response):
        raise ValidationError("Captcha is not correct")


def business_email_validator(email):
    email_split = email.split("@")
    if len(email_split) != 2:
        raise ValidationError("Wrong email is entered")
    if email_split[1] in PERSONAL_EMAIL_DOMAINS:
        raise ValidationError(
            "Please enter a business email associated with your company's domain."
        )


class ProtectedForm(forms.Form):
    visitor_id = forms.CharField(required=True)
    request_id = forms.CharField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        visitor_id = cleaned_data.get("visitor_id")
        request_id = cleaned_data.get("request_id")
        if not visitor_id or not request_id or not validate_visitor(visitor_id, request_id):
            raise ValidationError("Not allowed")
        return cleaned_data


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=265, required=True)
    last_name = forms.CharField(max_length=265, required=True)
    email = forms.EmailField(
        required=True,
        validators=[validators.EmailValidator(), business_email_validator],
    )
    password = forms.CharField(required=True)
    plan_type = forms.CharField(max_length=265, required=True, validators=[plan_type_validator])
    captcha = forms.CharField(required=True, validators=[captcha_validator])

    def clean_email(self):
        return self.cleaned_data["email"].lower()


class LoginForm(forms.Form):
    username = forms.EmailField(
        required=True,
        validators=[validators.EmailValidator(), business_email_validator],
    )
    password = forms.CharField(required=True)
    captcha = forms.CharField(required=True, validators=[captcha_validator])

    def clean_username(self):
        return self.cleaned_data["username"].lower()


class GoogleLoginForm(forms.Form):
    token_id = forms.CharField(required=True)
    plan_type = forms.CharField(max_length=265, required=False, validators=[plan_type_validator])


class VerifyEmailForm(forms.Form):
    token = forms.CharField(required=True, max_length=265)


class ResetPasswordForm(forms.Form):
    token = forms.CharField(required=True, max_length=265)
    password = forms.CharField(required=True)


class SendResetPasswordForm(forms.Form):
    email = forms.EmailField(required=True, validators=[validators.EmailValidator()])

    def clean_email(self):
        return self.cleaned_data["email"].lower()


class ChangePasswordForm(forms.Form):
    password = forms.CharField(required=True)


class DeleteAccountForm(forms.Form):
    delete_reason = forms.CharField(required=True)


class TaskForm(forms.Form):
    task = forms.CharField(required=True)
