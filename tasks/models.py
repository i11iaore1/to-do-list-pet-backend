from django.db import models
from django.utils import timezone


class Task(models.Model):
    description = models.TextField()
    is_closed = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_current(self):
        return self.due_date is None or self.due_date >= timezone.now()

    def __str__(self):
        return f"{self.pk} {self.description[:20]}"


class UserTask(Task):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
