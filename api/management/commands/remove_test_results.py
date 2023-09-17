from django.core.management.base import BaseCommand

from api import models

TEST_CASES = [
    {"first_name": "samuel", "last_name": "beek", "domain_name": "veed.io"},
    {
        "first_name": "charlie",
        "middle_name": "g",
        "last_name": "kirkconnell",
        "domain_name": "caymanenterprisecity.com",
    },
    {"first_name": "helen", "last_name": "spiegel", "domain_name": "cima.ky"},
    {"first_name": "jay", "last_name": "mumtaz", "domain_name": "biizy.com"},
    {"first_name": "dylan", "last_name": "bostock", "domain_name": "swpcayman.com"},
    {"first_name": "anna", "last_name": "krendzelakova", "domain_name": "harneys.com"},
    {"first_name": "anna", "last_name": "ghandilyan", "domain_name": "artexrisk.com"},
    {"first_name": "rahul", "last_name": "swani", "domain_name": "aerispartners.com"},
    {
        "first_name": "david",
        "middle_name": "w",
        "last_name": "joncas",
        "domain_name": "aerispartners.com",
    },
    {"first_name": "george", "last_name": "wauchope", "domain_name": "emailchaser.io"},
]


class Command(BaseCommand):
    help = "Remove all results of test case"

    def handle(self, *args, **options):
        for test in TEST_CASES:
            models.SearchResult.objects.filter(**test).delete()
