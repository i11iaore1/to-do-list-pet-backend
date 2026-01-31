from tasks.exceptions import TaskStatusError, TaskError


def update_task(task, fields):
    """
    Expects Task Object and field dict
    """
    if not fields:
        return task

    if task.is_expired:
        raise TaskStatusError("Task is expired", "expired")

    if task.status == task.StatusChoices.CLOSED:
        raise TaskStatusError("Task is already closed.", "closed")

    if "status" in fields:
        raise TaskError("Task status can not be changed manually.")

    for field, value in fields.items():
        setattr(task, field, value)

    task.save(update_fields=["updated_at", *fields.keys()])

    return task


def delete_task(task):
    if task.is_expired:
        raise TaskStatusError("Task is expired", "expired")

    task.delete()


def close_task(task):
    """
    Expects Task Object
    """
    if task.is_expired:
        raise TaskStatusError("Task is expired", "expired")

    if task.status == task.StatusChoices.CLOSED:
        raise TaskStatusError("Task is already closed.", "closed")

    task.status = task.StatusChoices.CLOSED
    task.save(update_fields=["status", "updated_at"])

    return task


def reissue_task(task, new_due_date):
    """
    Expects Task Object and validated datetime
    """
    if task.status == task.StatusChoices.ISSUED:
        if task.due_date is None or not task.is_expired:
            raise TaskStatusError("Task is currently issued and not expired.", "active")

    task.status = task.StatusChoices.ISSUED
    task.due_date=new_due_date
    task.save(update_fields=["status", "due_date", "updated_at"])

    return task
