class TaskError(Exception):
    def __init__(self, message, code="task_error"):
        super().__init__(message)

        self.message = message
        self.code = code


class TaskStatusError(TaskError):
    def __init__(self, message, status):
        super().__init__(
            message=message,
            code=f"task_{status}"
        )
