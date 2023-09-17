from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from basic_auth import models


def getFieldsModel(model):
    return [field.name for field in model._meta.get_fields()]


class UserPlanInline(admin.TabularInline):
    model = models.UserPlan
    can_delete = False
    extra = 0


@admin.register(models.User)
class MyUserAdmin(UserAdmin):
    list_display = [
        "email",
        "first_name",
        "last_name",
        "google_auth",
        "is_active",
        "search_credits",
        "is_superuser",
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                    "is_superuser",
                    "is_verified",
                    "is_active",
                    "google_auth",
                    "date_joined",
                    "delete_reason",
                )
            },
        ),
        ("Personal info", {"fields": ("first_name", "last_name")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_filter = ("is_superuser", "is_active")
    inlines = [
        UserPlanInline,
    ]
    ordering = ("email",)


@admin.register(models.Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["plan_type", "price", "search_credits"]
