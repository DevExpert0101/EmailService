from rest_framework.permissions import BasePermission

from services.google_cloud_task import GOOGLE_TASK_SECRET
from services.turnstile import verify_turnstile_token


class IsPassedTurnstile(BasePermission):
    def has_permission(self, request, view):
        turnstile_token = request.META.get("HTTP_TURNSTILE_TOKEN")
        return turnstile_token and verify_turnstile_token(turnstile_token)


class IsAuthGoogleTask(BasePermission):
    def has_permission(self, request, view):
        return request.data.get("secret") == GOOGLE_TASK_SECRET
