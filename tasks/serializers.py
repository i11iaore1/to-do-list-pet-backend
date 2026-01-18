from django.utils import timezone
from rest_framework import serializers

from .models import UserTask


class UserTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTask
        fields = ("pk", "description", "status", "is_expired", "due_date", "created_at", "updated_at")

        read_only_fields = ("pk", "status", "is_expired", "created_at", "updated_at")

    def validate_due_date(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Task's due date must be in the future")

        return value
