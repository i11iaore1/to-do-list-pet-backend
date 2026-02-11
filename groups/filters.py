import django_filters
from django_filters.rest_framework import FilterSet

from .models import Group, Member, MemberTaskRelation

from tasks.filters import TaskFilter


class GroupFilter(FilterSet):
    class Meta:
        model = Group
        fields = {
            "name": ["icontains"]
        }

class MemberFilter(FilterSet):
    nickname = django_filters.CharFilter(
        field_name="nickname",
        lookup_expr="icontains"
    )

    class Meta:
        model = Member
        fields = {
            "role": ["exact"],
        }

class GroupTaskFilter(TaskFilter):
    creator = django_filters.NumberFilter(field_name="creator_id")


class MemberTaskRelationFilter(FilterSet):
    nickname = django_filters.CharFilter(
        field_name="nickname",
        lookup_expr="icontains"
    )

    class Meta:
        model = MemberTaskRelation
        fields = ["can_edit"]
