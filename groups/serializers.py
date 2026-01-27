from rest_framework import serializers

from .models import Group, GroupTask, Member, MemberTaskRelation


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("pk", "name", "created_at", "updated_at")
        read_only_fields = ("pk", "created_at", "updated_at")


class CreateMemberSerializer(serializers.ModelSerializer):
    """
    ONLY FOR DESEREALIZATION\n
    takes in (user, role)
    and can only update an account
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

    user_nickname = serializers.CharField(source="user.nickname", read_only=True)

    class Meta:
        model = Member
        fields = ("pk", "user_nickname", "nickname", "group", "role", "joined_at", "updated_at")
        read_only_fields = fields
