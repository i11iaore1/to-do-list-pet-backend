from rest_framework import serializers

from .models import UserTask
from .validators import validate_future_date


class StaffUserTaskSerializer(serializers.ModelSerializer):
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = UserTask
        fields = "__all__"

        read_only_fields = ("pk", "created_at", "updated_at")

    def validate_due_date(self, value):
        return validate_future_date(value, "Task's due date must be in the future")


class UserTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTask
        fields = ("pk", "description", "status", "is_expired", "due_date", "created_at", "updated_at")

        read_only_fields = ("pk", "status", "created_at", "updated_at")

    def validate_due_date(self, value):
        return validate_future_date(value, "Task's due date must be in the future")


class ReissuedUserTaskSerializer(serializers.ModelSerializer):
    due_date = serializers.DateTimeField(required=True, allow_null=True)

    class Meta(UserTaskSerializer.Meta):
        model = UserTask
        fields = ("pk", "description", "status", "is_expired", "due_date", "created_at", "updated_at")
        read_only_fields = ("pk", "description", "status", "is_expired", "created_at", "updated_at")

    def validate_due_date(self, value):
        return validate_future_date(value, "Task's due date must be in the future")
