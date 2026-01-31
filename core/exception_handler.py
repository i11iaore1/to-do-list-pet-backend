from django.utils import timezone

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from tasks.exceptions import TaskError
# from groups.exceptions import MembershipError


def custom_exception_handler(exception, context):
    response = exception_handler(exception, context)

    if response is None:
        if isinstance(exception, (
            TaskError,
            # MembershipError
        )):
            response = Response(
                {
                    "detail":exception.message,
                    "code":exception.code
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    if response is not None:
        response.data["timestampz"] = timezone.now()

    return response
