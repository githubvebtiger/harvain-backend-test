from django import http
from django.db import models
from drf_spectacular import utils as drf_utils
from rest_framework import permissions as rest_permissions
from rest_framework import renderers as rest_renderers
from rest_framework import response as rest_response
from rest_framework import status as rest_status

from football.services.prefetch import PrefetchView
from utils.third_party.api.rest_framework import mixins as utils_mixins
from user.permissions import IsNotBlocked

from .... import models as bets_models
from ..serializers import serializers as bets_serializers
from . import filters as frontend_filters


class OddsAmountViewSet(utils_mixins.PrefetchableListMixin):
    permission_classes = []

    @drf_utils.extend_schema(
        description="NO AUTH. Get sports that have games in it.",
        responses=bets_serializers.ReadOddsAmountSerializer,
    )
    def list(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        queryset = self._prefetch_list(queryset=self.queryset)
        return rest_response.Response(data={"types": queryset}, status=rest_status.HTTP_200_OK)

    def _prefetch_list(self, queryset: models.QuerySet) -> list:
        return PrefetchView()._count_fixtures(queryset=queryset)

    serializer_class = bets_serializers.ReadOddsAmountSerializer

    renderer_classes = [rest_renderers.JSONRenderer]
    queryset = bets_models.Odds.objects


class BetsViewSet(utils_mixins.PrefetchableListMixin):
    permission_classes = [rest_permissions.IsAuthenticated, IsNotBlocked]

    @drf_utils.extend_schema(
        description="USER AUTH. Get all bets (in progress, wins and losses)",
        responses=bets_serializers.ReadBetSerializer,
    )
    def list(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        return super().list(request=request, *args, **kwargs)

    serializer_class = bets_serializers.ReadBetSerializer

    renderer_classes = [rest_renderers.JSONRenderer]
    queryset = bets_models.Bet.objects

    renderer_classes = [rest_renderers.JSONRenderer]
    queryset = bets_models.Bet.objects

    filterset_class = frontend_filters.BetsFilterSet


class TradeViewSet(utils_mixins.PrefetchableListMixin):
    permission_classes = [rest_permissions.IsAuthenticated, IsNotBlocked]

    def _get_client(self):
        """Get the Client for the current user (whether logged in as Client or Satellite)."""
        user = self.request.user
        if hasattr(user, 'satellite') and hasattr(user.satellite, 'satellite_client'):
            return user.satellite.satellite_client
        return user

    @drf_utils.extend_schema(
        description="SATELLITE AUTH. Get trade history.",
        responses=bets_serializers.ReadTradeSerializer,
    )
    def list(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        return super().list(request=request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        client = self._get_client()
        return queryset.filter(client=client)

    serializer_class = bets_serializers.ReadTradeSerializer

    renderer_classes = [rest_renderers.JSONRenderer]
    queryset = bets_models.Trade.objects
