from tasks.exceptions import TaskStatusError, TaskError


def update_task(task, fields):
    """
    Expects Task Object and field dict
    """
    if not fields:
        return task

    if task.is_closed:
        raise TaskStatusError("Task is closed and can not be updated. Reissue this task to update it.", "closed")

    if task.is_due_date_passed:
        raise TaskStatusError("Task is expired and can not be updated. Reissue this task to update it.", "expired")

    if "is_closed" in fields:
        raise TaskError("Task status can not be changed manually.")

    for field, value in fields.items():
        setattr(task, field, value)

    task.save(update_fields=["updated_at", *fields.keys()])

    return task


def delete_task(task):
    """
    Expects Task Object
    """

    task.delete()


def close_task(task):
    """
    Expects Task Object
    """
    # if task.is_due_date_passed:
    #     raise TaskStatusError("Task is expired and can not be closed.", "expired")

    if task.is_closed:
        raise TaskStatusError("Task is already closed.", "closed")

    task.is_closed = True
    task.save(update_fields=["is_closed", "updated_at"])

    return task


def reissue_task(task, new_due_date):
    """
    Expects Task Object and validated datetime
    """
    if not task.is_closed and not task.is_due_date_passed:
        raise TaskStatusError("Task is currenty active and can not be reissued.", "active")

    task.is_closed = False
    task.due_date=new_due_date
    task.save(update_fields=["is_closed", "due_date", "updated_at"])

    return task
