from django.db import transaction

from rest_framework.exceptions import PermissionDenied


def create_group_task(request_user, group, task_data):
    request_user_membership = group.members.filter(
        user=request_user
    ).first()

    if not request_user.is_staff:
        if not request_user_membership:
            raise PermissionDenied("You are not a member of this group.")

    with transaction.atomic():
        # membership of the request user may be None if staff and not a group member
        new_group_task = group.tasks.create(
            **task_data,
            creator=request_user_membership
        )

        if request_user_membership is not None:
            new_group_task.related_members.create(
                member=request_user_membership,
                can_edit=True
            )

    return new_group_task
