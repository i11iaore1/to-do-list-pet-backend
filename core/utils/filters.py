from django.utils import timezone
from django.db.models import Q


def filter_tasks_by_status(tasks, status):
    class StatusChoices:
        ACTIVE = "active"
        EXPIRED = "expired"
        CLOSED = "closed"

    if status == StatusChoices.CLOSED:
        tasks = tasks.filter(is_closed=True)
    else:
        now = timezone.now()
        tasks = tasks.filter(is_closed=False)

        if status == StatusChoices.ACTIVE:
            tasks = tasks.filter(
                Q(due_date__gte=now) | Q(due_date__isnull=True)
            )
        elif status == StatusChoices.EXPIRED:
            tasks = tasks.filter(
                due_date__lt=now
            )

    return tasks
