from rest_framework import serializers

from api import models


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = "__all__"


class OptOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OptOutRequest
        fields = ["full_name", "email"]

    def validate_email(self, value):
        return value.strip().lower()
