from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from core.pagination import NormalDataPagination

from .models import Group, GroupTask, Member, MemberTaskRelation
from .serializers import GroupSerializer, MemberInfoSerializer, CreateMemberSerializer, UpdateMemberSerializer, GroupTaskSeriaizer
from .permissions import GroupPermissions
from .services.membership_management import create_member, update_member_role, delete_member


class GroupListView(GenericAPIView):
    queryset = Group.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = GroupSerializer
    pagination_class = NormalDataPagination

    def get(self, request, *args, **kwargs):
        queryset = Group.objects.filter(members__user=request.user)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            group = serializer.save()
            Member.objects.create(user=request.user, group=group, role=Member.RoleChoices.OWNER)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class GroupDetailView(GenericAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes =  [IsAuthenticated]
        elif self.request.method in ("PATCH", "PUT", "DELETE"):
            permission_classes =  [GroupPermissions.IsGroupOwnerOrStaff]
        else:
            permission_classes = [IsAuthenticated]
        return [permission_class() for permission_class in permission_classes]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

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
    pagination_class = NormalDataPagination

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
        return MemberInfoSerializer

    def get(self, request, *args, **kwargs):
        group = get_object_or_404(Group, pk=self.kwargs["pk"])
        self.check_object_permissions(request, group)

        queryset = group.members.select_related("user").all()
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

        return Response(
            MemberInfoSerializer(new_member).data,
            status=status.HTTP_201_CREATED
        )


class MemberDetailView(GenericAPIView):
    queryset = Member.objects.all()

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
        return MemberInfoSerializer

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
