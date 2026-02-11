from django import http
from django.db import models as django_models
from drf_spectacular import utils as drf_utils
from rest_framework import mixins as rest_mixins
from rest_framework import permissions as rest_permissions
from rest_framework import renderers as rest_renderers
from rest_framework import response as rest_response

from utils.third_party.api.rest_framework import mixins as utils_mixins
from user.permissions import IsNotBlocked

from ..... import models as user_models
from ..serializers import serializers as user_serializers


class RequisitesViewSet(
    utils_mixins.PrefetchableListMixin,
    rest_mixins.CreateModelMixin,
    rest_mixins.UpdateModelMixin,
    rest_mixins.DestroyModelMixin,
):

    renderer_classes = [rest_renderers.JSONRenderer]
    queryset = user_models.Requisites.objects

    serializer_class = user_serializers.ReadRequisitesSerializer

    def _get_client(self):
        """Get the Client for the current user (whether logged in as Client or Satellite)."""
        user = self.request.user
        # Check if user is a Satellite (request.user is User, but has .satellite reverse relation)
        if hasattr(user, 'satellite') and hasattr(user.satellite, 'satellite_client'):
            return user.satellite.satellite_client
        # Otherwise, assume user is a Client
        return user

    def get_queryset(self):
        queryset = super().get_queryset()
        client = self._get_client()
        return queryset.filter(client=client)

    @drf_utils.extend_schema(
        description="USER AUTH. Get satellite withdrawal requisites.",
        responses=user_serializers.ReadRequisitesSerializer,
    )
    def list(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        return super().list(request, *args, **kwargs)

    @drf_utils.extend_schema(
        description="USER AUTH. Create satellite withdrawal requisites.",
        responses=user_serializers.ReadRequisitesSerializer,
    )
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["client"] = request.user
        request._full_data = data

        return super().create(request, *args, **kwargs)

    @drf_utils.extend_schema(
        description="USER AUTH. Update satellite withdrawal requisites.",
        responses=user_serializers.ReadRequisitesSerializer,
    )
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        data = request.data.copy()
        data["client"] = request.user
        request._full_data = data
        return super().update(request, *args, **kwargs)

    @drf_utils.extend_schema(
        description="USER AUTH. Update satellite withdrawal requisites.",
        responses=user_serializers.ReadRequisitesSerializer,
    )
    def partial_update(self, request, *args, **kwargs):
        data = request.data.copy()
        data["client"] = request.user
        request._full_data = data
        return super().partial_update(request, *args, **kwargs)

    @drf_utils.extend_schema(
        description="USER AUTH. Destroy satellite withdrawal requisites.",
        responses=user_serializers.ReadRequisitesSerializer,
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def _prefetch_list(self, queryset: django_models.QuerySet) -> django_models.QuerySet:
        client = self._get_client()
        return queryset.filter(client=client)

    permission_classes = [rest_permissions.IsAuthenticated, IsNotBlocked]
