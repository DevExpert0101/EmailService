from rest_framework import serializers

from basic_auth import models


class PlanSerializer(serializers.ModelSerializer):
    plan_days = serializers.SerializerMethodField()

    class Meta:
        model = models.Plan
        fields = [
            "id",
            "plan_type",
            "price",
            "search_credits",
            "verify_credits",
            "plan_days",
        ]

    def get_plan_days(self, obj):
        return obj.get_days()


class UserPlanSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()

    class Meta:
        model = models.UserPlan
        fields = [
            "id",
            "plan",
            "status",
            "search_credits",
            "verify_credits",
            "created_at",
            "updated_at",
        ]


class UserSerializer(serializers.ModelSerializer):
    plan_data = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "plan_data",
            "avatar",
            "is_verified",
            "date_joined",
            "google_auth",
            "unverified_changed_email",
            "completed_tasks",
        ]

    def get_plan_data(self, obj):
        return UserPlanSerializer(obj.get_plan_data()).data

    def update(self, instance, validated_data):
        new_email = validated_data.get("email")
        if new_email:
            del validated_data["email"]
            new_email = new_email.strip().lower()
        if new_email == instance.email:
            new_email = None

        if new_email and models.User.objects.filter(email=new_email).first():
            raise serializers.ValidationError(
                {"errors": {"email": "The email has been used in another account"}}
            )
        user = super().update(instance, validated_data)
        if new_email:
            user.unverified_changed_email = new_email
            user.save()
            user.send_email_for_changing()
        return user
