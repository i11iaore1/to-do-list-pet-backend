from django.utils import timezone

import django_filters

from .models import Task


class TaskFilter(django_filters.FilterSet):
    closed = django_filters.BooleanFilter(field_name="is_closed")
    current = django_filters.BooleanFilter(method="filter_current")
    due_date_range = django_filters.DateTimeFromToRangeFilter(field_name="due_date")

    class Meta:
        model = Task
        fields = {
            "due_date": ["lt", "gt", "date"],
            "description": ["contains"]
        }

    def filter_current(self, queryset, name, value):
        now = timezone.now()

        if value:
            return queryset.exclude(due_date__lt=now)
        return queryset.filter(due_date__lt=now)
