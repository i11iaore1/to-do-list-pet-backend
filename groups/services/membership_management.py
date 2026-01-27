from django.db import transaction

from rest_framework.exceptions import ValidationError, PermissionDenied

from groups.models import Member


def transfer_group_ownership(new_owner):
    """
    Takes in a Member object
    """

    with transaction.atomic():
        group = new_owner.group
        current_owner = Member.objects.select_for_update().filter(
            group=group,
            role=Member.RoleChoices.OWNER
        ).first()

        if current_owner:
            current_owner.role = Member.RoleChoices.ADMIN
            current_owner.save()

        new_owner.role = Member.RoleChoices.OWNER
        new_owner.save()

def create_member(request_user, group, target_user_id, role):
    if not request_user.is_staff:
        request_user_membership = Member.objects.filter(user=request_user, group=group).first()

        if not request_user_membership:
            raise PermissionDenied("You are not a member of this group.")

        if request_user_membership.role not in Member.ADMIN_ROLES:
            raise PermissionDenied("You are not allowed to add members to this group.")

        if request_user_membership.role == Member.RoleChoices.ADMIN:
            if role in Member.ADMIN_ROLES:
                raise PermissionDenied("You are not allowed to assign this role.")

    with transaction.atomic():
        new_member = Member.objects.create(group=group, user_id=target_user_id, role=role)
        if role == Member.RoleChoices.OWNER:
            transfer_group_ownership(new_member)

    return new_member

def update_member_role(request_user, target_member, role):
    with transaction.atomic():
        if not request_user.is_staff:
            request_user_membership = Member.objects.filter(user=request_user, group=target_member.group).first()

            if not request_user_membership:
                raise PermissionDenied("You are not a member of this group.")

            if request_user_membership.role != Member.RoleChoices.OWNER:
                raise PermissionDenied("You are not allowed to manage roles in this group.")

        if target_member.role == Member.RoleChoices.OWNER:
            if role != Member.RoleChoices.OWNER:
                raise ValidationError({"detail":"A group should always have an owner. Transfer ownership instead."})

        if role == Member.RoleChoices.OWNER and target_member.role != Member.RoleChoices.OWNER:
            transfer_group_ownership(target_member)
        else:
            if target_member.role != role:
                target_member.role = role
                target_member.save()

    return target_member

def delete_member(request_user, target_member):
    is_trying_to_leave = request_user == target_member.user

    if is_trying_to_leave and target_member.role != Member.RoleChoices.OWNER:
        target_member.delete()
        return

    if not request_user.is_staff:
        group = target_member.group
        request_user_membership = Member.objects.filter(
            user=request_user,
            group=group
        ).first()

        if not request_user_membership:
            raise PermissionDenied("You are not a member of this group.")

        if request_user_membership.role not in Member.ADMIN_ROLES:
            raise PermissionDenied("You are not allowed to remove other users from this group.")

        if request_user_membership.role == Member.RoleChoices.ADMIN:
            if target_member.role in Member.ADMIN_ROLES:
                raise PermissionDenied("You are not allowed to remove users with this role from this group.")

    if target_member.role == Member.RoleChoices.OWNER:
        raise ValidationError({"detail":"A group should always have an owner. Transfer ownership first."})

    target_member.delete()
