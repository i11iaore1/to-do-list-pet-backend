from rest_framework.permissions import BasePermission

from .models import Member

class GroupPermissions:
    class ObjectTypes:
        GROUP = "group"
        MEMBER = "member"

    object_to_group_mapper = {
        ObjectTypes.GROUP: lambda obj: obj,
        ObjectTypes.MEMBER: lambda obj: obj.group,
    }

    @staticmethod
    def __create_group_resourse_permission(object_type, roles=None, check_membership_ownership=False):
        class GroupPermission(BasePermission):
            def has_permission(self, request, view):
                return bool(request.user and request.user.is_authenticated)

            def has_object_permission(self, request, view, obj):
                if request.user.is_staff:
                    return True

                if object_type in GroupPermissions.object_to_group_mapper:
                    group = GroupPermissions.object_to_group_mapper[object_type](obj)
                else:
                    raise NotImplementedError(f"{object_type} is not defined in group_object_mapper")

                if check_membership_ownership and object_type == GroupPermissions.ObjectTypes.MEMBER:
                    if request.user == obj.user:
                        return True

                membership = group.members.filter(
                    user=request.user
                ).first()

                if roles is None:
                    return bool(membership)

                return bool(membership and membership.role in roles)

        GroupPermission.__name__ = f"GroupPermission_{object_type}_{"_".join(roles) if roles else ""}"
        return GroupPermission


    IsGroupMemberOrStaff = __create_group_resourse_permission(
        object_type=ObjectTypes.GROUP
    )

    IsGroupAdminOrStaff = __create_group_resourse_permission(
        object_type=ObjectTypes.GROUP,
        roles=Member.ADMIN_ROLES
    )

    IsGroupOwnerOrStaff = __create_group_resourse_permission(
        object_type=ObjectTypes.GROUP,
        roles=[Member.RoleChoices.OWNER]
    )

    IsMembersGroupMemberOrStaff = __create_group_resourse_permission(
        object_type=ObjectTypes.MEMBER
    )

    IsMembersGroupAdminOrStaff = __create_group_resourse_permission(
        object_type=ObjectTypes.MEMBER,
        roles=Member.ADMIN_ROLES
    )

    IsMembersGroupOwnerOrStaff = __create_group_resourse_permission(
        object_type=ObjectTypes.MEMBER,
        roles=[Member.RoleChoices.OWNER]
    )

    IsMembershipOwnerOrMembersGroupAdminOrStaff = __create_group_resourse_permission(
        object_type=ObjectTypes.MEMBER,
        roles=Member.ADMIN_ROLES,
        check_membership_ownership=True
    )


class GroupTaskPermissions:
    class TaskRelations:
        CREATOR = "creator"
        EDITOR = "editor"
        RELATED = "related"

    @staticmethod
    def __create_group_task_permission(task_relation):
        class GroupTaskPermission(BasePermission):
            def has_permission(self, request, view):
                return bool(request.user and request.user.is_authenticated)

            def has_object_permission(self, request, view, obj):
                # staff
                if request.user.is_staff:
                    return True

                request_user_membership = obj.group.members.filter(
                    user=request.user
                ).first()

                if not request_user_membership:
                    return False

                # group admin
                if request_user_membership.role in Member.ADMIN_ROLES:
                    return True

                # task creator
                if task_relation == GroupTaskPermissions.TaskRelations.CREATOR:
                    if obj.creator == request_user_membership:
                        return True
                else:
                    request_member_relation = obj.related_members.filter(
                        member=request_user_membership
                    ).first()

                    if not request_member_relation:
                        return False

                    # editor
                    if task_relation == GroupTaskPermissions.TaskRelations.EDITOR:
                        if request_member_relation.can_edit:
                            return True

                    # related
                    elif task_relation == GroupTaskPermissions.TaskRelations.RELATED:
                        # relation existance was previously checked
                        return True

                return False

        GroupTaskPermission.__name__ = f"GroupTask{task_relation.capitalize()}Permission"
        return GroupTaskPermission


    IsTaskRelatedOrGroupAdminOrStaff = __create_group_task_permission(
        task_relation=TaskRelations.RELATED
    )

    IsTaskEditorOrGroupAdminOrStaff = __create_group_task_permission(
        task_relation=TaskRelations.EDITOR
    )

    IsTaskCreatorOrGroupAdminOrStaff = __create_group_task_permission(
        task_relation=TaskRelations.CREATOR
    )


class IsTargetMemberOrTaskCreatorOrGroupAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # staff
        if request.user.is_staff:
            return True

        request_user_membership = obj.member.group.members.filter(
            user=request.user
        ).first()

        if not request_user_membership:
            return False

        # group admin
        if request_user_membership.role in Member.ADMIN_ROLES:
            return True

        # task creator
        if obj.group_task.creator == request_user_membership:
            return True

        # target member
        return request_user_membership == obj.member
