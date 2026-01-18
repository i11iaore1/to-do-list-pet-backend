from django.db import models
from django.utils import timezone


class Task(models.Model):
    class StatusChoices(models.TextChoices):
        ISSUED = "issued"
        CLOSED = "closed"

    description = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.ISSUED
    )
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_expired(self):
        if self.due_date:
            return self.due_date < timezone.now() and self.status != self.StatusChoices.CLOSED
        return False

    def __str__(self):
        return f"{self.pk} {self.description[:20]}"


class UserTask(Task):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
