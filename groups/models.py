from django.db import models
from tasks.models import Task


class Group(models.Model):
    name = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk} {self.name}"


class GroupTask(Task):
    creator = models.ForeignKey("groups.Member", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.pk}"


class Member(models.Model):
    class RoleChoices(models.TextChoices):
        ADMIN = "admin"
        OWNER = "owner"

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="memberships")
    group = models.ForeignKey("groups.Group", on_delete=models.CASCADE, related_name="members")
    role = models.CharField(null=True, blank=True, max_length=10, choices=RoleChoices.choices)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'group'], name='unique_user_group')
        ]

    def __str__(self):
        return f"{self.pk} {self.user} {self.group}"


class MemberTaskRelation(models.Model):
    member = models.ForeignKey(
        "groups.Member",
        on_delete=models.CASCADE,
        related_name="related_group_tasks"
    )
    group_task = models.ForeignKey(
        "groups.GroupTask",
        on_delete=models.CASCADE,
        related_name="related_members"
    )
    can_close = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["member", "group_task"],
                name="unique_member_group_task"
            )
        ]

    def __str__(self):
        return f"{self.member}"
