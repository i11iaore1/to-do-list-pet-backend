from django.db import transaction
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from core.pagination import NormalDataPagination
from .models import UserTask
from .serializers import TaskInfoSerializer, UserTaskInfoSerializer, InputTaskSerializer, TaskReissueSerializer
from .permissions import IsTaskOwnerOrStaff
from .services.task_management import update_task, delete_task, close_task, reissue_task
from .filters import TaskFilter


User = get_user_model()


class UserTaskListView(generics.GenericAPIView):
    is_admin_route = False

    queryset = UserTask.objects.all()
    pagination_class = NormalDataPagination
    filterset_class = TaskFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    ordering_filters = ["due_date", "created_at"]
    ordering = ["due_date"]

    def get_permissions(self):
        if self.is_admin_route:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]

        return [permission_class() for permission_class in permission_classes]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return InputTaskSerializer
        return TaskInfoSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        if self.is_admin_route:
            return UserTask.objects.filter(user_id=self.kwargs["pk"])
        return UserTask.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_task_data = serializer.validated_data

        if self.is_admin_route:
            target_user = get_object_or_404(User, pk=kwargs["pk"])
        else:
            target_user = request.user

        new_task = UserTask.objects.create(
            user=target_user,
            **user_task_data
        )

        return Response(
            TaskInfoSerializer(new_task).data,
            status=status.HTTP_201_CREATED
        )


class UserTaskDetailView(generics.GenericAPIView):
    queryset = UserTask.objects.all()
    serializer_class = UserTaskInfoSerializer
    permission_classes = [IsTaskOwnerOrStaff]

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return InputTaskSerializer
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        user_task = update_task(instance, serializer.validated_data)

        return Response(self.serializer_class(user_task).data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_task(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)


# Task state management views

class TaskCloseView(generics.GenericAPIView):
    def get_permissions(self):
        raise NotImplementedError(f"Implement get_permissions in {self.__class__}")

    def get_queryset(self):
        raise NotImplementedError(f"Implement get_queryset in {self.__class__}")

    def get_serializer_class(self):
        raise NotImplementedError(f"Implement get_serializer_class in {self.__class__}")

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            task = get_object_or_404(self.get_queryset().select_for_update(), pk=kwargs["pk"])
            self.check_object_permissions(request, task)
            task = close_task(task)

            return Response(self.get_serializer(task).data)


class TaskReissueView(generics.GenericAPIView):
    def get_permissions(self):
        raise NotImplementedError(f"Implement get_permissions in {self.__class__}")

    def get_queryset(self):
        raise NotImplementedError(f"Implement get_queryset in {self.__class__}")

    def get_serializer_class(self):
        raise NotImplementedError(f"Implement get_serializer_class in {self.__class__}")

    def post(self, request, *args, **kwargs):
        serializer = TaskReissueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            task = get_object_or_404(self.get_queryset().select_for_update(), pk=kwargs["pk"])
            self.check_object_permissions(request, task)

            task = reissue_task(
                task,
                serializer.validated_data["due_date"]
            )

            return Response(self.get_serializer(task).data)


class UserTaskCloseView(TaskCloseView):
    def get_permissions(self):
        return [IsTaskOwnerOrStaff()]

    def get_queryset(self):
        return UserTask.objects.all()

    def get_serializer_class(self):
        return TaskInfoSerializer


class UserTaskReissueView(TaskReissueView):
    def get_permissions(self):
        return [IsTaskOwnerOrStaff()]

    def get_queryset(self):
        return UserTask.objects.all()

    def get_serializer_class(self):
        return TaskInfoSerializer
