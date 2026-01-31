from rest_framework import serializers

from .models import UserTask, Task
from .validators import validate_future_date


class BaseTaskSerializer(serializers.ModelSerializer):
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = ("pk", "description", "status", "is_expired", "due_date", "created_at", "updated_at")
        read_only_fields = ("pk", "created_at", "updated_at")

    def validate_due_date(self, value):
        return validate_future_date(value, "Task's due date must be in the future")


class TaskInfoSerializer(BaseTaskSerializer):
    """
    ONLY FOR SEREALIZATION\n
    returns (pk, description, status, is_expired, due_date, created_at, updated_at)
    """
    class Meta(BaseTaskSerializer.Meta):
        read_only_fields = BaseTaskSerializer.Meta.fields


class UserTaskInfoSerializer(TaskInfoSerializer):
    """
    ONLY FOR SEREALIZATION\n
    returns (pk, description, status, is_expired, due_date, user_id, created_at, updated_at)
    """
    user_id = serializers.IntegerField(source="user.pk", read_only=True)

    class Meta(TaskInfoSerializer.Meta):
        model = UserTask
        fields = TaskInfoSerializer.Meta.fields + ("user_id", )


class InputTaskSerializer(BaseTaskSerializer):
    """
    ONLY FOR DESEREALIZATION\n
    expects (due_date)
    """
    class Meta(BaseTaskSerializer.Meta):
        fields = ("description", "due_date")

        extra_kwargs = {
            "description": {"write_only":True},
            "due_date": {"write_only":True}
        }


class ReissuingTaskSerializer(BaseTaskSerializer):
    """
    ONLY FOR DESEREALIZATION\n
    expects (due_date)
    """
    # due_date = serializers.DateTimeField(required=True, allow_null=True)

    class Meta(BaseTaskSerializer.Meta):
        fields = ("due_date", )

        extra_kwargs = {
            "due_date": {"write_only": True}
        }
