from django.db import models


class Task(models.Model):
    class StatusChoices(models.TextChoices):
        ISSUED = "issued"
        CLOSED = "closed"
        EXPIRED = "expired"

    description = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.ISSUED
    )
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk} {self.description[:20]}"


class UserTask(Task):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
