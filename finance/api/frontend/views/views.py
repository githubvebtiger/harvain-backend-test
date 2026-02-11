from django import http
from drf_spectacular import utils as drf_utils
from rest_framework import permissions as rest_permissions
from rest_framework import renderers as rest_renderers
from rest_framework import response as rest_response

from utils.third_party.api.rest_framework import mixins as utils_mixins
from user.permissions import IsNotBlocked

from .... import models as finance_models
from ..serializers import serializers as finance_serializers


class TransactionViewSet(utils_mixins.PrefetchableListMixin):
    permission_classes = [rest_permissions.IsAuthenticated, IsNotBlocked]

    def _get_client(self):
        """Get the Client for the current user (whether logged in as Client or Satellite)."""
        user = self.request.user
        if hasattr(user, 'satellite') and hasattr(user.satellite, 'satellite_client'):
            return user.satellite.satellite_client
        return user

    @drf_utils.extend_schema(
        description="SATELLITE AUTH. Get all transactions (refill, withdraw).",
        parameters=[
            drf_utils.OpenApiParameter(
                name="type",
                description="refill or withdraw",
                required=True,
                type=drf_utils.OpenApiTypes.STR,
            )
        ],
        responses=finance_serializers.ReadTransactionSerializer,
    )
    def list(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        return super().list(request=request, *args, **kwargs)

    def get_queryset(self):
        type = self.request.GET.get("type")
        client = self._get_client()

        if type:
            if type == "refill":
                return super().get_queryset().filter(type=1, client=client)
            elif type == "withdraw":
                return super().get_queryset().filter(type=2, client=client)

        return super().get_queryset()

    serializer_class = finance_serializers.ReadTransactionSerializer

    renderer_classes = [rest_renderers.JSONRenderer]
    queryset = finance_models.Transaction.objects.order_by("-created_at")
