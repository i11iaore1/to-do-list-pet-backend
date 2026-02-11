from rest_framework import serializers

from .models import Group, GroupTask, Member, MemberTaskRelation
from tasks.serializers import TaskInfoSerializer


# GROUP

class GroupListSerializer(serializers.ModelSerializer):
    joined_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Group
        fields = ("pk", "name", "created_at", "updated_at", "joined_at")
        read_only_fields = ("pk", "created_at", "updated_at")


class GroupDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("pk", "name", "created_at", "updated_at")
        read_only_fields = ("pk", "created_at", "updated_at")


# MEMBER

class CreateMemberSerializer(serializers.ModelSerializer):
    """
    ONLY FOR DESEREALIZATION\n
    takes in (user, role)
    and can only create an account
    """
    class Meta:
        model = Member
        fields = ("user", "role")

        extra_kwargs = {
            "user": {'write_only': True},
            "role": {'write_only': True}
        }


class UpdateMemberSerializer(serializers.ModelSerializer):
    """
    ONLY FOR DESEREALIZATION\n
    takes in (role)
    and can only update an account
    """
    class Meta:
        model = Member
        fields = ("role", )

        extra_kwargs = {
            "role": {'write_only': True}
        }


class MemberInfoSerializer(serializers.ModelSerializer):
    """
    ONLY FOR SERIALIZATION\n
    returns (pk, user, nickname, group, role, joined_at, updated_at)
    """
    nickname = serializers.CharField(source="user.nickname", read_only=True)

    class Meta:
        model = Member
        fields = ("pk", "nickname", "group", "role", "joined_at", "updated_at")
        read_only_fields = fields


# GROUP TASK

class GroupTaskInfoSerializer(TaskInfoSerializer):
    """
    ONLY FOR SEREALIZATION\n
    returns (pk, description, is_closed, is_current, due_date, creator, created_at, updated_at)
    """
    creator = MemberInfoSerializer(read_only=True)

    class Meta(TaskInfoSerializer.Meta):
        model = GroupTask
        fields = TaskInfoSerializer.Meta.fields + ("group_id", "creator")


# MemberTaskRelation

class MemberTaskRelationCreateSerializer(serializers.ModelSerializer):
    """
    ONLY FOR DESEREALIZATION\n
    expects (member, can_edit)
    """
    class Meta:
        model = MemberTaskRelation
        fields = ("member", "can_edit")
        extra_kwargs = {
            "member": {'write_only': True},
            "can_edit": {'write_only': True}
        }


class MemberTaskRelationUpdateSerializer(serializers.ModelSerializer):
    """
    ONLY FOR DESEREALIZATION\n
    expects (can_edit)
    """
    class Meta:
        model = MemberTaskRelation
        fields = ("can_edit", )
        extra_kwargs = {
            "can_edit": {'write_only': True}
        }


class MemberTaskRelationListSerializer(serializers.ModelSerializer):
    """
    ONLY FOR SEREALIZATION\n
    returns (pk, member, group_task, can_edit, created_at, updated_at)\n
    Is used for group_task_detail
    """
    member = MemberInfoSerializer(read_only=True)

    class Meta:
        model = MemberTaskRelation
        fields = ("pk", "member", "can_edit", "created_at", "updated_at")
        read_only_fields = fields


class MemberTaskRelationDetailSerializer(serializers.ModelSerializer):
    """
    ONLY FOR SEREALIZATION\n
    returns (pk, member, group_task, can_edit, created_at, updated_at)
    """
    member = MemberInfoSerializer(read_only=True)
    group_task = GroupTaskInfoSerializer(read_only=True)

    class Meta:
        model = MemberTaskRelation
        fields = ("pk", "member", "group_task", "can_edit", "created_at", "updated_at")
        read_only_fields = fields


class MemberTaskRelationMinimalDetailSerializer(serializers.ModelSerializer):
    """
    ONLY FOR SEREALIZATION\n
    returns (pk, member, group_task, can_edit, created_at, updated_at)
    """
    member = serializers.IntegerField(source="member.pk", read_only=True)
    group_task = serializers.IntegerField(source="group_task.pk", read_only=True)

    class Meta:
        model = MemberTaskRelation
        fields = ("pk", "member", "group_task", "can_edit", "created_at", "updated_at")
        read_only_fields = fields
