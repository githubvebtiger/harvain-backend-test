import typing

from django import http
from django.db import models

# region				-----External Imports-----
from rest_framework import mixins as rest_mixins
from rest_framework import response as rest_response
from rest_framework import viewsets as rest_viewsets

# endregion

# region				-----Internal Imports-----
# endregion

# region			  -----Supporting Variables-----
# endregion


class PrefetchableRetrieveMixin(
    rest_viewsets.GenericViewSet, rest_mixins.RetrieveModelMixin
):
    def _prefetch_retrieve(self, queryset: models.QuerySet) -> models.QuerySet:
        return queryset

    def retrieve(
        self, request: http.HttpRequest, *args, **kwargs
    ) -> rest_response.Response:
        # * Calling prefetching function for adding necessary additions
        self.queryset: models.QuerySet = self._prefetch_retrieve(queryset=self.queryset)

        return super().retrieve(request, *args, **kwargs)


class PrefetchableListMixin(rest_viewsets.GenericViewSet, rest_mixins.ListModelMixin):
    def _prefetch_list(self, queryset: models.QuerySet) -> models.QuerySet:
        return queryset

    def list(
        self, request: http.HttpRequest, *args, **kwargs
    ) -> rest_response.Response:
        # * Calling prefetching function for adding necessary additions
        self.queryset: models.QuerySet = self._prefetch_list(queryset=self.queryset)

        return super().list(request, *args, **kwargs)


class PrefetchableOutputMixin(object):
    def _prefetch_output(self, queryset: models.QuerySet) -> models.QuerySet:
        return queryset


class DynamicSerializersViewSet(rest_viewsets.GenericViewSet):
    serializer_classes: typing.Dict = {}
    default_serializer_class = None

    def get_serializer_class(self) -> typing.Callable:
        return self.serializer_classes.get(self.action) or self.default_serializer_class
