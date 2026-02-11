from groups.exceptions import GroupError


def create_member_task_relation(group_task, target_member, can_edit):
    if target_member.group != group_task.group:
        raise GroupError("This member is from another group.", "another_group_member")

    if group_task.related_members.filter(
        member=target_member
    ).exists():
        raise GroupError("This member already has permission for this task.", "already_has_permission")

    return group_task.related_members.create(
        member=target_member,
        can_edit=can_edit
    )
