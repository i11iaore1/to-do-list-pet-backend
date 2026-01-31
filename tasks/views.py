from django.db import transaction
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from core.utils.filters import filter_tasks_by_status
from core.pagination import NormalDataPagination
from .models import UserTask
from .serializers import TaskInfoSerializer, UserTaskInfoSerializer, InputTaskSerializer, ReissuingTaskSerializer
from .permissions import IsTaskOwnerOrStaff
from .services.task_management import update_task, delete_task, close_task, reissue_task


User = get_user_model()


class UserTaskListView(generics.GenericAPIView):
    is_admin_route = False

    queryset = UserTask.objects.all()
    pagination_class = NormalDataPagination

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
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        if self.is_admin_route:
            queryset = UserTask.objects.filter(user_id=self.kwargs["pk"])
        else:
            queryset = UserTask.objects.filter(user=self.request.user)

        task_status = self.request.query_params.get("status")
        if task_status:
            queryset = filter_tasks_by_status(queryset, task_status)

        return queryset

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
    permission_classes = [IsTaskOwnerOrStaff]
    response_serializer = UserTaskInfoSerializer

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return InputTaskSerializer
        return self.response_serializer

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        user_task = update_task(instance, serializer.validated_data)

        return Response(self.response_serializer(user_task).data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_task(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserTaskClosureView(generics.GenericAPIView):
    queryset = UserTask.objects.all()
    permission_classes = [IsTaskOwnerOrStaff]
    serializer_class = UserTaskInfoSerializer

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_queryset().select_for_update().get(pk=kwargs["pk"])
            self.check_object_permissions(request, instance)
            close_task(instance)

            serializer = self.get_serializer(instance)

            return Response(serializer.data)


class UserTaskReissueView(generics.GenericAPIView):
    queryset = UserTask.objects.all()
    permission_classes = [IsTaskOwnerOrStaff]
    serializer_class = ReissuingTaskSerializer
    response_serializer = UserTaskInfoSerializer

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_queryset().select_for_update().get(pk=self.kwargs["pk"])
            self.check_object_permissions(request, instance)

            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            user_task = reissue_task(instance, serializer.validated_data["due_date"])

            return Response(self.response_serializer(user_task).data)
