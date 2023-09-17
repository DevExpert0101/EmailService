import logging
import os

import rest_framework.authtoken.models as authtoken_models
import rest_framework.authtoken.serializers as authtoken_serializers
import rest_framework.authtoken.views as authtoken_views
import rest_framework.permissions as rest_permissions
import rest_framework.views as rest_views
from django.urls import reverse
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from basic_auth import forms, models, serializers
from basic_auth.constants import (
    FOLLOWING_EMAIL_AFER_SIGN_UP_TIMEOUT,
    NOT_ALLOW_PERSONAL_EMAIL_MESSAGE,
)
from services import email as email_service
from services import utils
from services.google_cloud_task import BASE_TASK_URL, create_google_task

logger = logging.getLogger(__name__)


class LoginView(authtoken_views.ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        form = forms.LoginForm(request.data)
        if not form.is_valid():
            return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)
        user = models.User.objects.filter(email=form.cleaned_data["username"]).first()
        if not user:
            return Response(
                {"errors": {"username": ["The email you entered isn’t connected to an account."]}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = authtoken_serializers.AuthTokenSerializer(
            data=form.cleaned_data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            if user.is_superuser:
                return Response(
                    {"message": "Wrong email or password"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            token, _ = authtoken_models.Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "user": serializers.UserSerializer(user).data})
        else:
            return Response(
                {"message": "Wrong email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(rest_views.APIView):
    permission_classes = (rest_permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response({"message": "Logout successfully"})


class UserView(generics.RetrieveUpdateAPIView):
    permission_classes = (rest_permissions.IsAuthenticated,)
    serializer_class = serializers.UserSerializer

    def get_object(self):
        user = self.request.user
        if (
            utils.get_utc_now() - user.plan_data.updated_at
        ).days >= user.plan_data.plan.get_days():
            user.clear_credits()
        return user


@api_view(["POST"])
def register(request):
    form = forms.RegisterForm(request.data)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        user = models.User.objects.filter(email=cleaned_data["email"]).first()
        if user:
            return Response(
                {"errors": {"email": ["The email has been taken"]}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = models.create_user(
            cleaned_data["plan_type"],
            cleaned_data["email"],
            cleaned_data["password"],
            first_name=cleaned_data["first_name"],
            last_name=cleaned_data["last_name"],
        )

        # Send following email after 2 minutes
        create_google_task(
            f"{BASE_TASK_URL}{reverse('send_following_email_afer_sign_up')}",
            {"user_id": user.id},
            FOLLOWING_EMAIL_AFER_SIGN_UP_TIMEOUT,
        )
        token, _ = authtoken_models.Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": serializers.UserSerializer(user).data})
    else:
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([rest_permissions.IsAuthenticated])
def send_email_verify_account(request):
    request.user.send_email_verification_url()
    return Response({"message": "Success"})


@api_view(["POST"])
def verify_account(request):
    form = forms.VerifyEmailForm(request.data)
    if form.is_valid():
        user = models.User.objects.filter(token=form.cleaned_data["token"]).first()
        if user:
            user.verify_user()
            token, _ = authtoken_models.Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "user": serializers.UserSerializer(user).data})
        else:
            return Response({"message": "Can not find user"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def send_email_reset_password(request):
    form = forms.SendResetPasswordForm(request.data)
    if form.is_valid():
        user = models.User.objects.filter(email=form.cleaned_data["email"]).first()
        if user:
            user.send_forgot_password_url()
            return Response({"message": "Success"})
        else:
            return Response(
                {"message": "The email doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def reset_password(request):
    form = forms.ResetPasswordForm(request.data)
    if form.is_valid():
        user = models.User.objects.filter(token=form.cleaned_data["token"]).first()
        if user:
            user.change_password(form.cleaned_data["password"])
            return Response({"message": "Success"})
        else:
            return Response({"message": "Can not find user"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def change_email(request):
    form = forms.VerifyEmailForm(request.data)
    if form.is_valid():
        user = models.User.objects.filter(token=form.cleaned_data["token"]).first()
        if user and user.unverified_changed_email:
            if models.User.objects.filter(email=user.unverified_changed_email).first():
                return Response(
                    {"message": "The email has been used in another account"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.email = user.unverified_changed_email
            user.unverified_changed_email = None
            user.save()
            return Response({"message": "Success"})
        else:
            return Response({"message": "Can not find user"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def google_login(request):
    form = forms.GoogleLoginForm(data=request.data)
    if form.is_valid():
        try:
            idinfo = id_token.verify_oauth2_token(
                form.cleaned_data["token_id"],
                requests.Request(),
                os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
            )

            try:
                forms.business_email_validator(idinfo["email"])
            except Exception:
                return Response(
                    {"message": NOT_ALLOW_PERSONAL_EMAIL_MESSAGE},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = models.User.objects.filter(email=idinfo["email"]).first()
            if not user:
                plan_type = form.cleaned_data["plan_type"]
                if not plan_type:
                    plan_type = models.Plan.TRIAL
                user = models.create_user(
                    plan_type,
                    idinfo["email"],
                    first_name=idinfo["given_name"],
                    last_name=idinfo["family_name"],
                    avatar=idinfo["picture"],
                    google_auth=True,
                    is_verified=True,
                )
                create_google_task(
                    f"{BASE_TASK_URL}{reverse('send_following_email_afer_sign_up')}",
                    {"user_id": user.id},
                    2 * 60,
                )
            elif not user.is_active:
                return Response(
                    {"message": f"The account {user.email} has been deleted."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token, _ = authtoken_models.Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "user": serializers.UserSerializer(user).data})
        except Exception as e:
            logger.error(f"Error when login using google {str(e)}")
            return Response(
                {"message": "Somethings went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )
    return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([rest_permissions.IsAuthenticated])
def change_password(request):
    form = forms.ChangePasswordForm(request.data)
    if form.is_valid():
        user = request.user
        user.set_password(form.cleaned_data["password"])
        user.save()
        return Response({"message": "success"})
    return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([rest_permissions.IsAuthenticated])
def delete_account(request):
    form = forms.DeleteAccountForm(request.data)
    if form.is_valid():
        user = request.user
        user.is_active = False
        user.delete_reason = form.cleaned_data["delete_reason"]
        user.save()
        user.auth_token.delete()
        email_service.send_email(
            email_service.AUTOMATIC_EMAIL[0],
            "An Emailchaser account has been deleted",
            email_service.DELETE_NOTIFICATION_FOR_ADMIN_EMAIL.format(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                delete_reason=user.delete_reason,
            ),
            reply_to=user.email,
        )
        return Response({"message": "success"})
    return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes([rest_permissions.IsAuthenticated])
def update_account(request):
    user = request.user
    serializer = serializers.UserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"user": serializer.data})
    return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([rest_permissions.IsAuthenticated])
def complete_task(request):
    form = forms.TaskForm(request.data)
    if form.is_valid():
        tasks = request.user.completed_tasks
        if form.cleaned_data["task"] not in tasks:
            tasks.append(form.cleaned_data["task"])
            request.user.completed_tasks = tasks
            request.user.save()
        return Response({"completed_tasks": request.user.completed_tasks})
    return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)
