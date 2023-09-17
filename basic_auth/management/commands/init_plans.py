from django.core.management.base import BaseCommand

from basic_auth import constants, models


class Command(BaseCommand):
    help = "Init 3 plans"

    def handle(self, *args, **options):
        models.Plan.objects.create(
            plan_type=models.Plan.TRIAL,
            price=7,
            search_credits=constants.DEFAULT_SEARCH_CREDITS_TRIAL_ACCOUNT,
        )
        models.Plan.objects.create(
            plan_type=models.Plan.ANNUAL_NORMAL,
            price=708,
            search_credits=constants.DEFAULT_SEARCH_CREDITS_ANNUAL_NORMAL_ACCOUNT,
        )
        models.Plan.objects.create(
            plan_type=models.Plan.ANNUAL_ENTERPRISE,
            price=0,
            search_credits=0,
        )
