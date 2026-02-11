from django import http
from django.db import models
from django_filters import rest_framework as filters

# region				-----External Imports-----
from rest_framework import filters as rest_filters
from rest_framework import views

# endregion


class RequisitesFilterBackend(rest_filters.BaseFilterBackend):
    def filter_queryset(
        self, request: http.HttpRequest, queryset: models.QuerySet, view: views.APIView
    ) -> models.QuerySet:
        return queryset
