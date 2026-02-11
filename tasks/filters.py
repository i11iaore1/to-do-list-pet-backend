from django.utils import timezone
from django.db.models import Q, F

from rest_framework.filters import OrderingFilter

import django_filters
from django_filters.rest_framework import FilterSet

from .models import Task


class TaskFilter(FilterSet):
    closed = django_filters.BooleanFilter(field_name="is_closed")
    current = django_filters.BooleanFilter(method="filter_current")
    due_date = django_filters.DateFilter(field_name="due_date", lookup_expr="date")
    due_date_after = django_filters.DateTimeFilter(method="filter_due_date_after")
    due_date_before = django_filters.DateTimeFilter(field_name="due_date", lookup_expr="lt")
    no_due_date = django_filters.BooleanFilter(field_name="due_date", lookup_expr="isnull")
    description = django_filters.CharFilter(field_name="description", lookup_expr="icontains")

    class Meta:
        model = Task
        fields = []

    def filter_current(self, queryset, name, value):
        now = timezone.now()

        if value:
            return queryset.filter(
                Q(due_date__gte=now) | Q(due_date__isnull=True)
            )
        return queryset.filter(due_date__lt=now)

    def filter_due_date_after(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(due_date__gte=value) | Q(due_date__isnull=True)
            )
        return queryset

class TaskOrderingFilter(OrderingFilter):
    # treats due_date=None as bigger date (no due date)
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            for idx, field in enumerate(ordering):
                if "due_date" in field:
                    if field.startswith("-"):
                        # due_date desc
                        ordering[idx] = F("due_date").desc(nulls_first=True)
                    else:
                        # due_date asc
                        ordering[idx] = F("due_date").asc(nulls_last=True)

            return queryset.order_by(*ordering)

        return queryset
