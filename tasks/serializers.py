from django.utils import timezone
from rest_framework import serializers

from .models import UserTask


class UserTaskSerializer(serializers.ModelSerializer):
    # status = serializers.CharField(read_only=True) # because i want special views to manage task statuses

    class Meta:
        model = UserTask
        fields = ("pk", "description", "status", "due_date", "user", "created_at", "updated_at")

        read_only_fields = ("pk", "status", "created_at", "updated_at")

    def validate_due_date(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Task's due date must be in the future")

        return value
