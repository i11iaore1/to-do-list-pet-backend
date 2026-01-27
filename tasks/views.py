from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from core.utils.filters import filter_tasks_by_status
from core.pagination import NormalDataPagination
from .models import UserTask
from .serializers import UserTaskSerializer, StaffUserTaskSerializer, ReissuedUserTaskSerializer
from .permissions import IsTaskOwner, IsTaskOwnerOrStaff


class UserTaskListView(generics.GenericAPIView):
    queryset = UserTask.objects.all()
    permission_classes = (IsAdminUser, )
    serializer_class = StaffUserTaskSerializer
    pagination_class = NormalDataPagination

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def get_queryset(self):
        user = self.kwargs["pk"]
        print(user)
        queryset = UserTask.objects.filter(user=user)

        task_status = self.request.query_params.get("status")
        if task_status:
            queryset = filter_tasks_by_status(queryset, task_status)

        return queryset


class UserTaskSingleView(generics.GenericAPIView):
    queryset = UserTask.objects.all()
    permission_classes = (IsTaskOwnerOrStaff, )
    serializer_class = UserTaskSerializer

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(
            serializer.data
        )

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserTaskPluralView(generics.GenericAPIView):
    queryset = UserTask.objects.all()
    permission_classes = (IsTaskOwner, )
    serializer_class = UserTaskSerializer
    pagination_class = NormalDataPagination

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        queryset = UserTask.objects.filter(user=user)

        task_status = self.request.query_params.get("status")
        if task_status:
            queryset = filter_tasks_by_status(queryset, task_status)

        return queryset

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class UserTaskClosureView(generics.GenericAPIView):
    queryset = UserTask.objects.all()
    permission_classes = (IsTaskOwnerOrStaff, )
    serializer_class = UserTaskSerializer

    def post(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status == UserTask.StatusChoices.CLOSED:
            return Response(
                {"detail":"Task is already closed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.status = UserTask.StatusChoices.CLOSED
        instance.save()
        serializer = self.get_serializer(instance)

        return Response(
            serializer.data
        )


class UserTaskReissueView(generics.GenericAPIView):
    queryset = UserTask.objects.all()
    permission_classes = (IsTaskOwnerOrStaff, )
    serializer_class = ReissuedUserTaskSerializer

    def post(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status == UserTask.StatusChoices.ISSUED:
            if instance.due_date is None or not instance.is_expired:
                return Response(
                    {"detail":"Task is currently issued and not expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(status=UserTask.StatusChoices.ISSUED)
        return Response(serializer.data)
