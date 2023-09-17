from django import forms
from django.core.exceptions import ValidationError

from basic_auth.constants import PERSONAL_EMAIL_DOMAINS
from email_finder.core.main import extract_domain
from services.fingerprint import validate_visitor
from utils.string import clean_trail_and_non_alphabit


def business_domain_validator(domain):
    if domain in PERSONAL_EMAIL_DOMAINS:
        raise ValidationError("Please enter a business domain.")


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


class FindEmailForm(ProtectedForm):
    first_name = forms.CharField(required=True)
    middle_name = forms.CharField(required=False)
    last_name = forms.CharField(required=True)
    domain_name = forms.CharField(required=True, validators=[business_domain_validator])

    def clean_first_name(self):
        return clean_trail_and_non_alphabit(self.cleaned_data["first_name"])

    def clean_middle_name(self):
        return clean_trail_and_non_alphabit(self.cleaned_data["middle_name"])

    def clean_last_name(self):
        return clean_trail_and_non_alphabit(self.cleaned_data["last_name"])

    def clean_domain_name(self):
        return extract_domain(self.cleaned_data["domain_name"])


class EmailVerifierForm(ProtectedForm):
    email = forms.EmailField(required=True)
