from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import UserTask
from .serializers import UserTaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = UserTask.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = UserTaskSerializer
