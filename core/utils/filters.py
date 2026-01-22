from django.utils import timezone
from django.db.models import Q

from tasks.models import Task


def filter_tasks_by_status(tasks, status):
    if status == Task.StatusChoices.CLOSED:
        tasks = tasks.filter(status=Task.StatusChoices.CLOSED)
    else:
        now = timezone.now()

        if status == Task.StatusChoices.ISSUED:
            tasks = tasks.filter(
                status=Task.StatusChoices.ISSUED
            ).filter(
                Q(due_date__gte=now) | Q(due_date__isnull=True)
            )
        elif status == "expired":
            tasks = tasks.exclude(
                status=Task.StatusChoices.CLOSED
            ).filter(
                due_date__lt=now
            )

    return tasks
