# region				-----External Imports-----
from django_filters import rest_framework as filters

# endregion


class ListNumberFilterSet(filters.BaseInFilter, filters.NumberFilter):
    pass


class ListStringFilterSet(filters.BaseInFilter, filters.CharFilter):
    pass
