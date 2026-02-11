class GroupError(Exception):
    def __init__(self, message, code="group_error"):
        super().__init__(message)

        self.message = message
        self.code = code
