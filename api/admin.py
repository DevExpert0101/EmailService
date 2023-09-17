from django.contrib import admin

from api import models


def getFieldsModel(model):
    return [field.name for field in model._meta.get_fields()]


@admin.register(models.AnonUser)
class AmonUserAdmin(admin.ModelAdmin):
    list_display = getFieldsModel(models.AnonUser)


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = getFieldsModel(models.Contact)


@admin.register(models.Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "link",
        "found_result",
        "zerobounce_api",
        "is_pwned",
        "social",
        "google_search",
        "additional_emails",
        "date_time",
    ]


class EmailFinderHistoryInline(admin.TabularInline):
    model = models.EmailFinderHistory
    extra = 0


@admin.register(models.SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "middle_name",
        "last_name",
        "domain_name",
        "result",
        "from_bulk_search",
        "created_at",
    ]

    inlines = [
        EmailFinderHistoryInline,
    ]


@admin.register(models.OptOutRequest)
class OptOutRequestAdmin(admin.ModelAdmin):
    list_display = [
        "full_name",
        "email",
    ]
