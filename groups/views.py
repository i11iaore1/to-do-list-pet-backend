from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from core.pagination import NormalDataPagination
from tasks.filters import TaskOrderingFilter
from tasks.views import TaskCloseView, TaskReissueView
from tasks.serializers import InputTaskSerializer, TaskInfoSerializer
from tasks.services.task_management import delete_task, update_task

from .models import Group, GroupTask, Member, MemberTaskRelation
from .serializers import GroupDetailSerializer, GroupListSerializer, MemberInfoSerializer, CreateMemberSerializer, MemberTaskRelationCreateSerializer, MemberTaskRelationMinimalDetailSerializer, MemberTaskRelationUpdateSerializer, UpdateMemberSerializer, GroupTaskInfoSerializer, MemberTaskRelationListSerializer, MemberTaskRelationDetailSerializer
from .permissions import GroupPermissions, GroupTaskPermissions, IsTargetMemberOrTaskCreatorOrGroupAdminOrStaff
from .filters import GroupFilter, GroupTaskFilter, MemberFilter, MemberTaskRelationFilter

from .services.membership_management import create_member, update_member_role, delete_member
from .services.group_task_management import create_group_task
from .services.member_task_relation_management import create_member_task_relation


User = get_user_model()


class GroupListView(GenericAPIView):
    is_admin_route = False

    queryset = Group.objects.all()
    serializer_class = GroupListSerializer
    pagination_class = NormalDataPagination

    filterset_class = GroupFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    ordering_fields = ["name", "joined_at"]
    ordering = ["-joined_at"]

    def get_permissions(self):
        if self.is_admin_route:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]

        return [permission_class() for permission_class in permission_classes]

    def get_queryset(self):
        if self.is_admin_route:
            user = get_object_or_404(User, pk=self.kwargs["pk"])
        else:
            user = self.request.user

        return Group.objects.filter(
            members__user=user
        ).annotate(
            joined_at=F("members__joined_at")
        )

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if self.is_admin_route:
            user = get_object_or_404(User, pk=kwargs["pk"])
        else:
            user = request.user

        with transaction.atomic():
            new_group = serializer.save()

            new_group.members.create(
                user = user,
                role=Member.RoleChoices.OWNER
            )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class GroupDetailView(GenericAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupDetailSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes =  [GroupPermissions.IsGroupMemberOrStaff]
        elif self.request.method in ("PATCH", "PUT", "DELETE"):
            permission_classes =  [GroupPermissions.IsGroupOwnerOrStaff]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        group_tasks = instance.get_relevant_tasks()

        if not request.user.is_staff:
            request_user_membership = instance.members.filter(
                user=request.user
            ).first()

            if not request_user_membership:
                raise PermissionDenied("You are not a member of this group.")

            # if not staff and not group admin, can see only related tasks
            # otherwise can se all tasks
            if not request_user_membership.role in Member.ADMIN_ROLES:
                group_tasks = group_tasks.filter(
                    related_members__member=request_user_membership
                )

        group_tasks = group_tasks.select_related("creator__user").order_by("due_date")
        members = instance.members.select_related("user").order_by("user__nickname")

        return Response(
            {
                **self.get_serializer(instance).data,
                "tasks": GroupTaskInfoSerializer(group_tasks[:10], many=True).data,
                "members": MemberInfoSerializer(members[:10], many=True).data
            }
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


class MemberListView(GenericAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberInfoSerializer
    pagination_class = NormalDataPagination

    filterset_class = MemberFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    ordering_fields = ["nickname", "joined_at"]
    ordering = ["joined_at"]

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [GroupPermissions.IsGroupMemberOrStaff]
        elif self.request.method == "POST":
            permission_classes = [GroupPermissions.IsGroupAdminOrStaff]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateMemberSerializer
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        group = get_object_or_404(Group, pk=self.kwargs["pk"])
        self.check_object_permissions(request, group)

        queryset = group.members.select_related("user").annotate(
            nickname=F("user__nickname")
        )
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        group = get_object_or_404(Group, pk=self.kwargs["pk"])
        self.check_object_permissions(request, group)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_member = create_member(
            request_user=request.user,
            group=group,
            target_user_id=serializer.validated_data["user"].id,
            role=serializer.validated_data["role"]
        )

        # CreateMemberSerializer has already made a DB-request to check if user exists
        new_member.user = serializer.validated_data["user"]

        return Response(
            MemberInfoSerializer(new_member).data,
            status=status.HTTP_201_CREATED
        )


class MemberDetailView(GenericAPIView):
    queryset = Member.objects.select_related("user")
    serializer_class = MemberInfoSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [GroupPermissions.IsMembersGroupMemberOrStaff]
        elif self.request.method in ("PATCH", "PUT"):
            permission_classes = [GroupPermissions.IsMembersGroupOwnerOrStaff]
        elif self.request.method == "DELETE":
            permission_classes = [GroupPermissions.IsMembershipOwnerOrMembersGroupAdminOrStaff]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return UpdateMemberSerializer
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        member = update_member_role(
            request_user=request.user,
            target_member=instance,
            role=serializer.validated_data["role"]
        )

        return Response(MemberInfoSerializer(member).data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        delete_member(
            request_user=request.user,
            target_member=instance
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupTaskListView(GenericAPIView):
    queryset = GroupTask.objects.select_related("creator__user")
    serializer_class = GroupTaskInfoSerializer
    pagination_class = NormalDataPagination

    permission_classes = [GroupPermissions.IsGroupMemberOrStaff]

    filterset_class = GroupTaskFilter
    filter_backends = [DjangoFilterBackend, TaskOrderingFilter]

    ordering_fields = ["due_date", "created_at"]
    ordering = ["due_date"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return InputTaskSerializer
        return self.serializer_class

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
        group = get_object_or_404(Group, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, group)

        queryset = self.queryset

        if not self.request.user.is_staff:
            request_user_membership = group.members.filter(
                user=self.request.user
            ).first()

            if not request_user_membership.role in Member.ADMIN_ROLES:
                queryset = queryset.filter(
                    related_members__member=request_user_membership
                )

        return queryset

    def post(self, request, *args, **kwargs):
        group = get_object_or_404(Group, pk=kwargs["pk"])
        self.check_object_permissions(request, group)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_group_task = create_group_task(
            request_user=request.user,
            group=group,
            task_data=serializer.validated_data
        )

        return Response(
            self.serializer_class(new_group_task).data,
            status=status.HTTP_201_CREATED
        )


class GroupTaskDetailView(GenericAPIView):
    queryset = GroupTask.objects.select_related(
        "group",
        "creator__user"
    ).prefetch_related(
        "related_members__member__user"
    )
    serializer_class = GroupTaskInfoSerializer

    def get_permissions(self):
        if self.request.method in ("PATCH", "PUT"):
            permission_classes = [GroupTaskPermissions.IsTaskEditorOrGroupAdminOrStaff]
        elif self.request.method == "DELETE":
            permission_classes = [GroupTaskPermissions.IsTaskCreatorOrGroupAdminOrStaff]
        elif self.request.method == "GET":
            permission_classes = [GroupTaskPermissions.IsTaskRelatedOrGroupAdminOrStaff]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return InputTaskSerializer
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        group_task = self.get_object()
        serializer = self.get_serializer(group_task)

        return Response(
            {
                **serializer.data,
                "related_members": MemberTaskRelationListSerializer(
                    group_task.related_members.all()[:10],
                    many=True
                ).data
            }
        )

    def patch(self, request, *args, **kwargs):
        with transaction.atomic():
            queryset = self.get_queryset().select_for_update()
            instance = get_object_or_404(queryset, pk=kwargs["pk"])

            self.check_object_permissions(request, instance)

            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            group_task = update_task(instance, serializer.validated_data)

        return Response(TaskInfoSerializer(group_task).data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_task(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupTaskCloseView(TaskCloseView):
    def get_permissions(self):
        return [GroupTaskPermissions.IsTaskEditorOrGroupAdminOrStaff()]

    def get_queryset(self):
        return GroupTask.objects.select_related("group")

    def get_serializer_class(self):
        return TaskInfoSerializer


class GroupTaskReissueView(TaskReissueView):
    def get_permissions(self):
        return [GroupTaskPermissions.IsTaskEditorOrGroupAdminOrStaff()]

    def get_queryset(self):
        return GroupTask.objects.select_related("group")

    def get_serializer_class(self):
        return TaskInfoSerializer


class MemberTaskRelationListView(GenericAPIView):
    queryset = MemberTaskRelation.objects.all()
    serializer_class = MemberTaskRelationListSerializer

    pagination_class = NormalDataPagination

    filterset_class = MemberTaskRelationFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    ordering_fields = ["created_at", "updated_at", "nickname"]
    ordering = ["created_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            permission_classes = [GroupTaskPermissions.IsTaskCreatorOrGroupAdminOrStaff]
        elif self.request.method == "GET":
            permission_classes = [GroupTaskPermissions.IsTaskRelatedOrGroupAdminOrStaff]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MemberTaskRelationCreateSerializer
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        group_task = get_object_or_404(
            GroupTask.objects.select_related("group"),
            pk=kwargs["pk"]
        )
        self.check_object_permissions(request, group_task)

        queryset = group_task.related_members.select_related("member__user").annotate(
            nickname=F("member__user__nickname")
        )
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        group_task = get_object_or_404(
            GroupTask.objects.select_related("group"),
            pk=kwargs["pk"]
        )
        self.check_object_permissions(request, group_task)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_member_task_relation = create_member_task_relation(
            group_task=group_task,
            target_member=serializer.validated_data["member"],
            can_edit=serializer.validated_data["can_edit"]
        )

        return Response(
            self.serializer_class(new_member_task_relation).data,
            status=status.HTTP_201_CREATED
        )


class MemberTaskRelationDetailView(GenericAPIView):
    queryset = MemberTaskRelation.objects.all().select_related(
        "group_task__group",
        "member__user"
    )
    serializer_class = MemberTaskRelationMinimalDetailSerializer

    def get_permissions(self):
        if self.request.method in ("PATCH", "PUT"):
            permission_classes = [GroupTaskPermissions.IsTaskCreatorOrGroupAdminOrStaff]
        elif self.request.method == "DELETE":
            permission_classes = [IsTargetMemberOrTaskCreatorOrGroupAdminOrStaff]
        elif self.request.method == "GET":
            permission_classes = [GroupTaskPermissions.IsTaskRelatedOrGroupAdminOrStaff]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return MemberTaskRelationUpdateSerializer
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        member_task_relation = get_object_or_404(
            MemberTaskRelation.objects.select_related(
                "member",
                "group_task"
            ),
            pk=kwargs["pk"]
        )
        self.check_object_permissions(
            request,
            member_task_relation.group_task
        )

        serializer = self.get_serializer(member_task_relation)

        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        with transaction.atomic():
            queryset = self.get_queryset().select_for_update()
            instance = get_object_or_404(queryset, pk=kwargs["pk"])

            self.check_object_permissions(request, instance.group_task)

            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(self.serializer_class(instance).data)

    def delete(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=kwargs["pk"])
        self.check_object_permissions(request, instance.group_task)

        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
