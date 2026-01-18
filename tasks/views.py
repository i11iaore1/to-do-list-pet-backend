from django.utils import timezone
from django.db.models import Q

from rest_framework import viewsets
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import UserTask
from .serializers import UserTaskSerializer, StaffUserTaskSerializer, ReissuedUserTaskSerializer
from .permissions import IsStaffOrTaskOwner


class StaffUserTaskViewSet(viewsets.ModelViewSet):
    queryset = UserTask.objects.all()
    permission_classes = (IsAdminUser, )
    serializer_class = StaffUserTaskSerializer


class UserTaskSingleView(generics.GenericAPIView):
    queryset = UserTask.objects.all()
    permission_classes = (IsStaffOrTaskOwner, )
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
    permission_classes = (IsStaffOrTaskOwner, )
    serializer_class = UserTaskSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        queryset = UserTask.objects.filter(user=user)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            if status_filter == UserTask.StatusChoices.CLOSED:
                queryset = queryset.filter(status=UserTask.StatusChoices.CLOSED)
            else:
                now = timezone.now()

                if status_filter == UserTask.StatusChoices.ISSUED:
                    queryset = queryset.filter(
                        status=UserTask.StatusChoices.ISSUED
                    ).filter(
                        Q(due_date__gte=now) | Q(due_date__isnull=True)
                    )
                elif status_filter == "expired":
                    queryset = queryset.exclude(
                        status=UserTask.StatusChoices.CLOSED
                    ).filter(
                        due_date__lt=now
                    )

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
    permission_classes = (IsStaffOrTaskOwner, )
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
    permission_classes = (IsStaffOrTaskOwner, )
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
