from django.utils import timezone
from dateutil.relativedelta import relativedelta

from django_filters import rest_framework as filters
from django.db.models import Q
from programs.models import (
    Child,
    ChildProgress,
    ChildEducation,
    EducationProgram,
)


class ChildFilter(filters.FilterSet):
    # search = filters.CharFilter(method="filter_search", label="Search")
    gender = filters.ChoiceFilter(
        choices=[("M", "MALE"), ("F", "FEMALE")], label="GENDER"
    )
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    LEFT = "LEFT"
    status = filters.ChoiceFilter(
        choices=[
            (ACTIVE, "Active"),
            (COMPLETED, "Completed"),
            (LEFT, "Left"),
        ],
        label="STATUS",
    )

    date_of_birth_after = filters.DateFilter(
        field_name="date_of_birth", lookup_expr="gte", label="Borned after"
    )
    date_of_birth_before = filters.DateFilter(
        field_name="date_of_birth", lookup_expr="lte", label="Borned before"
    )

    start_date_after = filters.DateFilter(
        field_name="start_date", lookup_expr="gte", label="Started after"
    )
    start_date_before = filters.DateFilter(
        field_name="start_date", lookup_expr="lte", label="Started before"
    )

    age_min = filters.NumberFilter(method="filter_age_min", label="minimum age")
    age_max = filters.NumberFilter(method="filter_age_max", label="maximum age")

    has_special_needs = filters.BooleanFilter(
        method="filter_special_needs", label="has special needs"
    )

    class Meta:
        model = Child
        fields = [
            "gender",
            "status",
            # "search",
            "date_of_birth_after",
            "date_of_birth_before",
            "start_date_after",
            "start_date_before",
            "age_min",
            "age_max",
            "has_special_needs",
        ]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(story__icontains=value)
        )

    def filter_age_min(self, queryset, name, value):
        max_date = timezone.now().date() - relativedelta(years=int(value))
        return queryset.filter(date_of_birth__lte=max_date)

    def filter_age_max(self, queryset, name, value):
        min_date = timezone.now().date() - relativedelta(years=int(value) + 1)
        return queryset.filter(date_of_birth__gte=min_date)

    def filter_special_needs(self, queryset, name, value):
        if value:
            return queryset.exclude(special_needs__isnull=True).exclude(
                special_needs__exact=""
            )
        else:
            return queryset.filter(
                Q(special_needs__isnull=True) | Q(special_needs__exact="")
            )


class ChildProgressFilter(filters.FilterSet):
    child = filters.NumberFilter(field_name="child__id", label="Child (ID)")
    child_name = filters.CharFilter(method="filter_child_name", label="Child Name")

    created_after = filters.DateFilter(
        field_name="created_on", lookup_expr="gte", label="Created after"
    )
    created_before = filters.DateFilter(
        field_name="created_on", lookup_expr="lte", label="Created before"
    )

    # search = filters.CharFilter(
    #     field_name="notes", lookup_expr="icontains", label="Search in the notes"
    # )
    has_media = filters.BooleanFilter(method="filter_has_media", label="Has medias")

    class Meta:
        model = ChildProgress
        fields = [
            "child",
            "child_name",
            "created_after",
            "created_before",
            # "search",
            "has_media",
        ]

    def filter_child_name(self, queryset, name, value):
        return queryset.filter(
            Q(child__first_name__icontains=value) | Q(child__last_name__icontains=value)
        )

    def filter_has_media(self, queryset, name, value):
        if value:
            return queryset.filter(progress_media__isnull=False).distinct()
        else:
            return queryset.filter(progress_media__isnull=True)


class EducationProgramFilter(filters.FilterSet):
    institution = filters.NumberFilter(
        field_name="institution__id", label="Institution (ID)"
    )
    institution_name = filters.CharFilter(
        field_name="institution__name",
        lookup_expr="icontains",
        label="Name of institution",
    )
    # search = filters.CharFilter(
    #     field_name="program_name", lookup_expr="icontains", label="Search by name"
    # )
    program_level = filters.CharFilter(lookup_expr="icontains", label="Program level")

    cost_min = filters.NumberFilter(
        field_name="cost", lookup_expr="gte", label="Cost minimum"
    )
    cost_max = filters.NumberFilter(
        field_name="cost", lookup_expr="lte", label="Cost maximum"
    )

    class Meta:
        model = EducationProgram
        fields = [
            "institution",
            "institution_name",
            # "search",
            "program_level",
            "cost_min",
            "cost_max",
        ]


class ChildEducationFilter(filters.FilterSet):
    child = filters.NumberFilter(field_name="child__id", label="Enfant (ID)")
    child_name = filters.CharFilter(method="filter_child_name", label="Name of child")
    program = filters.NumberFilter(field_name="program__id", label="Program (ID)")
    program_name = filters.CharFilter(
        field_name="program__program_name",
        lookup_expr="icontains",
        label="Name of the program",
    )

    institution = filters.NumberFilter(
        field_name="program__institution__id", label="Institution (ID)"
    )
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    DISCONTINUED = "DISCONTINUED"

    status = filters.ChoiceFilter(
        choices=[
            (ACTIVE, "Active"),
            (COMPLETED, "Completed"),
            (DISCONTINUED, "Discontinued"),
        ],
        label="Status",
    )

    start_date_after = filters.DateFilter(
        field_name="start_date", lookup_expr="gte", label="Started after"
    )
    start_date_before = filters.DateFilter(
        field_name="start_date", lookup_expr="lte", label="Stared before"
    )

    end_date_after = filters.DateFilter(
        field_name="end_date", lookup_expr="gte", label="Finished after"
    )
    end_date_before = filters.DateFilter(
        field_name="end_date", lookup_expr="lte", label="Finished before"
    )

    cost_min = filters.NumberFilter(
        field_name="cost", lookup_expr="gte", label="Minimum cost "
    )
    cost_max = filters.NumberFilter(
        field_name="cost", lookup_expr="lte", label="Maximum cosr"
    )

    is_active = filters.BooleanFilter(method="filter_is_active", label="is active")

    class Meta:
        model = ChildEducation
        fields = [
            "child",
            "child_name",
            "program",
            "program_name",
            "institution",
            "status",
            "start_date_after",
            "start_date_before",
            "end_date_after",
            "end_date_before",
            "cost_min",
            "cost_max",
            "is_active",
        ]

    def filter_child_name(self, queryset, name, value):
        return queryset.filter(
            Q(child__first_name__icontains=value) | Q(child__last_name__icontains=value)
        )

    def filter_is_active(self, queryset, name, value):
        today = timezone.now().date()
        if value:
            return queryset.filter(start_date__lte=today, status="ACTIVE").filter(
                Q(end_date__isnull=True) | Q(end_date__gte=today)
            )
        else:
            return queryset.exclude(start_date__lte=today, status="ACTIVE").exclude(
                Q(end_date__isnull=True) | Q(end_date__gte=today)
            )
