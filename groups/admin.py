from django.contrib import admin


from .models import Group, GroupTask, Member, MemberTaskRelation


admin.site.register(Group)
admin.site.register(GroupTask)
admin.site.register(Member)
admin.site.register(MemberTaskRelation)
