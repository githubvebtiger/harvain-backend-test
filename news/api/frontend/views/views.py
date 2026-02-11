from django import http
from drf_spectacular import utils as drf_utils
from rest_framework import mixins as rest_mixins
from rest_framework import renderers as rest_renderers
from rest_framework import response as rest_response
from rest_framework import viewsets as rest_viewsets

from .... import models as news_models
from ..serializers import serializers as news_serializers

cache_dictionary = {}


class NewsViewSet(rest_viewsets.GenericViewSet, rest_mixins.ListModelMixin):
    permission_classes = []

    @drf_utils.extend_schema(
        description="NO AUTH. Get all news.",
        parameters=[
            drf_utils.OpenApiParameter(
                name="header",
                description="Part of the new's header:",
                required=False,
                type=drf_utils.OpenApiTypes.STR,
            )
        ],
        responses=news_serializers.ReadNewsSerializer,
    )
    def list(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        return super().list(request=request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        if header := self.request.query_params.get('header', None):
            queryset = queryset.filter(header__icontains=header)
        return queryset.order_by("pk")

    serializer_class = news_serializers.ReadNewsSerializer
    renderer_classes = [rest_renderers.JSONRenderer]
    queryset = news_models.News.objects.all()
