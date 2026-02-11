from django import http, shortcuts
from django.db import models as django_models
from django.utils.translation import gettext_lazy as _
from drf_spectacular import utils as drf_utils
from rest_framework import mixins as rest_mixins
from rest_framework import permissions as rest_permissions
from rest_framework import renderers as rest_renderers
from rest_framework import response as rest_response
from rest_framework import status as rest_status
from rest_framework import viewsets as rest_viewsets

from utils.third_party.api.rest_framework import mixins as utils_mixins

from ..... import models as user_models
from ..serializers import serializers as satellite_serializers
from .....permissions import IsNotBlocked


class SatelliteAuthViewSet(rest_mixins.CreateModelMixin, utils_mixins.DynamicSerializersViewSet):
    permission_classes = [rest_permissions.IsAuthenticated, IsNotBlocked]

    @drf_utils.extend_schema(
        request=satellite_serializers.SatelliteAuthSerializer,
        description="Takes a set of satellite credentials and returns an access and refresh JSON web token pair to prove the authentication of those credentials.",
        responses=satellite_serializers.ReadSatelliteSerializer,
    )
    def create(self, request, *args, **kwargs):
        username = self.request.data.get("username", None)
        password = self.request.data.get("password", None)
        uuid = self.request.data.get("uuid", None)

        obj = shortcuts.get_object_or_404(self.queryset, satellite_client_id=self.request.user.id, username=username)

        # Use Django's secure password checking instead of plaintext comparison
        from django.contrib.auth.hashers import check_password
        if not check_password(password, obj.password):
            return rest_response.Response(
                data={"detail": "Incorrect username or password"},
                status=rest_status.HTTP_404_NOT_FOUND,
            )

        if not obj.allow_auth:
            return rest_response.Response(
                data={"detail": "No account with credentials"},
                status=rest_status.HTTP_400_BAD_REQUEST,
            )

        if obj.blocked:
            # Determine message based on verification status
            if obj.document_verified:
                # User is verified but blocked - show support message
                blocked_message = "Please contact technical support"
                can_verify = False
            else:
                # User is not verified - show verification message
                blocked_message = "Please verify your account"
                can_verify = True
            
            return rest_response.Response(
                data={
                    "detail": blocked_message, 
                    "blocked": True,
                    "can_verify": can_verify,
                    "document_verified": obj.document_verified,
                    "can_auto_unblock": not obj.document_verified
                },
                status=rest_status.HTTP_401_UNAUTHORIZED,
            )

        if obj.uuid != uuid:
            return rest_response.Response(
                data={"detail": "Incorrect username or password"},
                status=rest_status.HTTP_404_NOT_FOUND,
            )

        serialized_data = satellite_serializers.ReadSatelliteSerializer(instance=obj, many=False).data

        return rest_response.Response(data=serialized_data, status=rest_status.HTTP_200_OK)

    serializer_class = satellite_serializers.SatelliteAuthSerializer
    queryset = user_models.Satellite.objects


class SatelliteViewSet(
    utils_mixins.PrefetchableRetrieveMixin,
    utils_mixins.DynamicSerializersViewSet,
    rest_mixins.UpdateModelMixin,
):
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = shortcuts.get_object_or_404(queryset, id=self.kwargs.get("id"))
        self.check_object_permissions(self.request, obj)
        return obj

    @drf_utils.extend_schema(
        description="SATELLITE AUTH. Get info about satellite.", request=satellite_serializers.ReadSatelliteSerializer
    )
    def retrieve(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        return super().retrieve(request, *args, **kwargs)

    @drf_utils.extend_schema(
        description="SATELLITE AUTH. Change satellite info.", request=satellite_serializers.WriteSatelliteSerializer
    )
    def update(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        return super().update(request=request, *args, **kwargs)

    @drf_utils.extend_schema(
        description="SATELLITE AUTH. Change satellite info.", request=satellite_serializers.WriteSatelliteSerializer
    )
    def partial_update(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        return super().partial_update(request=request, *args, **kwargs)

    def _prefetch_retrieve(self, queryset: django_models.QuerySet) -> django_models.QuerySet:
        return queryset

    renderer_classes = [rest_renderers.JSONRenderer]
    queryset = user_models.Satellite.objects

    default_serializer_class = satellite_serializers.ReadSatelliteSerializer
    serializer_classes = {
        "partial_update": satellite_serializers.WriteSatelliteSerializer,
        "update": satellite_serializers.WriteSatelliteSerializer,
        "retrieve": satellite_serializers.ReadSatelliteSerializer,
    }

    permission_classes = [rest_permissions.IsAuthenticated, IsNotBlocked]

    lookup_field = "id"


class SatellitePasswordViewSet(rest_viewsets.GenericViewSet, rest_mixins.UpdateModelMixin):
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = shortcuts.get_object_or_404(queryset, id=self.request.user.id)
        self.check_object_permissions(self.request, obj)
        return obj

    @drf_utils.extend_schema(
        description="SATELLITE AUTH. Change satellite password.",
        request=satellite_serializers.WriteSatellitePasswordSerializer,
    )
    def update(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        return super().update(request=request, *args, **kwargs)

    @drf_utils.extend_schema(
        description="SATELLITE AUTH. Change satellite password.",
        request=satellite_serializers.WriteSatellitePasswordSerializer,
    )
    def partial_update(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        from django.contrib.auth.hashers import check_password

        serializer = self.serializer_class(data=self.request.data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            new_password = serializer.validated_data.pop("new_password")
            old_password = serializer.validated_data.pop("old_password")
            satellite = self.queryset.get(id=kwargs.get('pk', 0))

            # Use secure password checking instead of plaintext comparison
            if not check_password(old_password, satellite.password):
                return rest_response.Response(
                    data={"detail": "Wrong old password"},
                    status=rest_status.HTTP_400_BAD_REQUEST,
                )

            # Use set_password to properly hash the password
            satellite.set_password(new_password)
            # Keep password_visible for backward compatibility (DEPRECATED)
            satellite.password_visible = new_password
            satellite.save()
        return rest_response.Response(status=rest_status.HTTP_200_OK)

    serializer_class = satellite_serializers.WriteSatellitePasswordSerializer

    renderer_classes = [rest_renderers.JSONRenderer]
    queryset = user_models.Satellite.objects

    permission_classes = [rest_permissions.IsAuthenticated, IsNotBlocked]
