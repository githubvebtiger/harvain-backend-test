from django import http
from django.db import models
from drf_spectacular import utils as drf_utils
from rest_framework import renderers as rest_renderers
from rest_framework import response as rest_response
from rest_framework import status as rest_status

from utils.third_party.api.rest_framework import mixins as utils_mixins
from utils.third_party.api.rest_framework import paginators as utils_paginators

from .... import models as football_models
from ....services.prefetch import PrefetchView
from ..serializers import serializers as football_serializers

cache_dictionary = {}


class LeagueViewSet(utils_mixins.PrefetchableListMixin):
    permission_classes = []

    @drf_utils.extend_schema(
        parameters=[
            drf_utils.OpenApiParameter(
                name="kind_of_sport",
                description="ID of the sport: \
                    1 - football, 2 - baseball, 3 - basketball, 4 - formula1, \
                    5 - handball, 6 - hockey, 7 - rugby, 8 - volleyball",
                required=True,
                type=drf_utils.OpenApiTypes.INT,
            )
        ],
        description="NO AUTH. Get all games in specific kind of sport.",
        responses=football_serializers.ReadLeagueSerializer,
    )
    def list(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        key = f"sport_{request.GET.get('kind_of_sport')}"
        if key in cache_dictionary and "cache" not in request.GET:
            cached = cache_dictionary[key]
            return rest_response.Response(data=cached["data"], status=cached["status"])
        response = super().list(request=request, *args, **kwargs)
        if "cache" in request.GET:
            cache_dictionary[key] = {
                "data": response.data,
                "status": response.status_code,
            }
        return response

    def _prefetch_list(self, queryset: models.QuerySet) -> models.QuerySet:
        kind_of_sport = self.request.query_params.get("kind_of_sport")
        return PrefetchView()._prefetch_leagues(queryset=queryset, kind_of_sport=kind_of_sport)

    serializer_class = football_serializers.ReadLeagueSerializer

    pagination_class = utils_paginators.StandartPagePaginator
    renderer_classes = [rest_renderers.JSONRenderer]
    queryset = football_models.League.objects


class BestFixtureViewSet(utils_mixins.PrefetchableListMixin):

    permission_classes = []

    @drf_utils.extend_schema(
        parameters=[
            drf_utils.OpenApiParameter(
                name="kind_of_sport",
                description="ID of the sport: \
                    1 - football, 2 - baseball, 3 - basketball, 4 - formula1, \
                    5 - handball, 6 - hockey, 7 - rugby, 8 - volleyball",
                required=True,
                type=drf_utils.OpenApiTypes.INT,
            )
        ],
        description="NO AUTH. Get nearest game in specific kind of sport.",
        responses=football_serializers.ReadMatchSerializer,
    )
    def list(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        instance = self._prefetch_list(queryset=self.queryset)
        if instance:
            serialized_data = self.serializer_class(instance=instance, many=False).data
            return rest_response.Response(data=serialized_data, status=rest_status.HTTP_200_OK)
        return rest_response.Response(status=rest_status.HTTP_404_NOT_FOUND)

    def _prefetch_list(self, queryset: models.QuerySet) -> models.Model:
        kind_of_sport = self.request.query_params.get("kind_of_sport")
        return PrefetchView()._prefetch_best_fixture(queryset=queryset, kind_of_sport=kind_of_sport)

    serializer_class = football_serializers.ReadMatchSerializer
    renderer_classes = [rest_renderers.JSONRenderer]
    queryset = football_models.Match.objects
