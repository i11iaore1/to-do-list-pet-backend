from rest_framework.permissions import BasePermission

from .models import Member, MemberTaskRelation


class GroupResourceObjectTypes:
    GROUP = "group"
    MEMBER = "member"


object_to_group_mapper = {
    GroupResourceObjectTypes.GROUP: lambda obj: obj,
    GroupResourceObjectTypes.MEMBER: lambda obj: obj.group,
}


def create_group_resourse_permission(object_type, roles=None, check_membership_ownership=False):
    class GroupPermission(BasePermission):
        def has_permission(self, request, view):
            return bool(request.user and request.user.is_authenticated)

        def has_object_permission(self, request, view, obj):
            if request.user.is_staff:
                return True

            if object_type in object_to_group_mapper:
                group = object_to_group_mapper[object_type](obj)
            else:
                raise NotImplementedError(f"{object_type} is not defined in group_object_mapper")

            if check_membership_ownership and object_type == GroupResourceObjectTypes.MEMBER:
                if request.user == obj.user:
                    return True

            membership = group.members.filter(
                user=request.user
            ).first()

            if roles is None:
                return bool(membership)

            return bool(membership and membership.role in roles)

    GroupPermission.__name__ = f"GroupPermission_{object_type}_{roles}"
    return GroupPermission


class GroupPermissions:
    IsGroupMemberOrStaff = create_group_resourse_permission(
        object_type=GroupResourceObjectTypes.GROUP
    )

    IsGroupAdminOrStaff = create_group_resourse_permission(
        object_type=GroupResourceObjectTypes.GROUP,
        roles=Member.ADMIN_ROLES
    )

    IsGroupOwnerOrStaff = create_group_resourse_permission(
        object_type=GroupResourceObjectTypes.GROUP,
        roles=[Member.RoleChoices.OWNER]
    )

    IsMembersGroupMemberOrStaff = create_group_resourse_permission(
        object_type=GroupResourceObjectTypes.MEMBER
    )

    IsMembersGroupAdminOrStaff = create_group_resourse_permission(
        object_type=GroupResourceObjectTypes.MEMBER,
        roles=Member.ADMIN_ROLES
    )

    IsMembersGroupOwnerOrStaff = create_group_resourse_permission(
        object_type=GroupResourceObjectTypes.MEMBER,
        roles=[Member.RoleChoices.OWNER]
    )

    IsMembershipOwnerOrMembersGroupAdminOrStaff = create_group_resourse_permission(
        object_type=GroupResourceObjectTypes.MEMBER,
        roles=Member.ADMIN_ROLES,
        check_membership_ownership=True
    )
