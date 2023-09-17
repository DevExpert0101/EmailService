from django.urls import path

from basic_auth import views

urlpatterns = [
    path("user/", views.UserView.as_view(), name="user"),
    path("register/", views.register, name="register"),
    path(
        "send-email-verify-account/",
        views.send_email_verify_account,
        name="send_email_verify_account",
    ),
    path("verify-account/", views.verify_account, name="verify_account"),
    path("change-email/", views.change_email, name="change_email"),
    path(
        "send-email-reset-password/",
        views.send_email_reset_password,
        name="send_email_reset_password",
    ),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("login/google/", views.google_login, name="google_login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("change-password/", views.change_password, name="change_password"),
    path("delete-account/", views.delete_account, name="delete_account"),
    path("update-account/", views.update_account, name="update_account"),
    path("complete-task/", views.complete_task, name="complete_task"),
]
