from django import shortcuts, utils, views
from django.core import paginator as django_paginator
from django.db import models as django_models
from django.http import JsonResponse
from django.shortcuts import render
from django.template import loader

# region				-----External Imports-----
from django.utils.translation import gettext_lazy as _

from bets import models as bets_models

from . import models as football_models

# region				-----Internal Imports-----
from .services import prefetch as services_prefetch

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class FootballIndexView(services_prefetch.SportIndexView):
    template_name = "pages/football/index.html"

    def get(self, request, *args, **kwargs):
        leagues = self._prefetch_leagues(
            queryset=football_models.League.objects, kind_of_sport=1
        )
        best_fixture = self._prefetch_best_fixture(
            queryset=football_models.Match.objects, kind_of_sport=1
        )

        kwargs.update(
            best_fixture=best_fixture, page_title=_("Football"), leagues=leagues, type=1
        )

        return super().get(request=request, *args, **kwargs)


class BaseballIndexView(services_prefetch.SportIndexView):
    template_name = "pages/football/index.html"

    def get(self, request, *args, **kwargs):
        leagues = self._prefetch_leagues(
            queryset=football_models.League.objects, kind_of_sport=2
        )

        best_fixture = self._prefetch_best_fixture(
            queryset=football_models.Match.objects, kind_of_sport=2
        )

        kwargs.update(
            best_fixture=best_fixture, page_title=_("Baseball"), leagues=leagues, type=2
        )

        return super().get(request=request, *args, **kwargs)


class BasketballIndexView(services_prefetch.SportIndexView):
    template_name = "pages/football/index.html"

    def get(self, request, *args, **kwargs):
        leagues = self._prefetch_leagues(
            queryset=football_models.League.objects, kind_of_sport=3
        )

        best_fixture = self._prefetch_best_fixture(
            queryset=football_models.Match.objects, kind_of_sport=3
        )

        kwargs.update(
            best_fixture=best_fixture,
            page_title=_("BasketBall"),
            leagues=leagues,
            type=3,
        )

        return super().get(request=request, *args, **kwargs)


class Formula1IndexView(services_prefetch.SportIndexView):
    template_name = "pages/formula_1/index.html"

    def get(self, request, *args, **kwargs):
        leagues = self._prefetch_leagues(
            queryset=football_models.League.objects, kind_of_sport=4
        )

        best_fixture = self._prefetch_best_fixture(
            queryset=football_models.Match.objects, kind_of_sport=4
        )

        kwargs.update(
            best_fixture=best_fixture,
            page_title=_("Formula 1"),
            leagues=leagues,
            type=4,
        )

        return super().get(request=request, *args, **kwargs)


class HandballIndexView(services_prefetch.SportIndexView):
    template_name = "pages/football/index.html"

    def get(self, request, *args, **kwargs):
        leagues = self._prefetch_leagues(
            queryset=football_models.League.objects, kind_of_sport=5
        )

        best_fixture = self._prefetch_best_fixture(
            queryset=football_models.Match.objects, kind_of_sport=5
        )

        kwargs.update(
            best_fixture=best_fixture, page_title=_("Handball"), leagues=leagues, type=5
        )

        return super().get(request=request, *args, **kwargs)


class HockeyIndexView(services_prefetch.SportIndexView):
    template_name = "pages/football/index.html"

    def get(self, request, *args, **kwargs):
        leagues = self._prefetch_leagues(
            queryset=football_models.League.objects, kind_of_sport=6
        )

        best_fixture = self._prefetch_best_fixture(
            queryset=football_models.Match.objects, kind_of_sport=6
        )

        kwargs.update(
            best_fixture=best_fixture, page_title=_("Hockey"), leagues=leagues, type=6
        )

        return super().get(request=request, *args, **kwargs)


class RugbyIndexView(services_prefetch.SportIndexView):
    template_name = "pages/football/index.html"

    def get(self, request, *args, **kwargs):
        leagues = self._prefetch_leagues(
            queryset=football_models.League.objects, kind_of_sport=7
        )

        best_fixture = self._prefetch_best_fixture(
            queryset=football_models.Match.objects, kind_of_sport=7
        )

        kwargs.update(
            best_fixture=best_fixture, page_title=_("Rugby"), leagues=leagues, type=7
        )

        return super().get(request=request, *args, **kwargs)


class VolleyballIndexView(services_prefetch.SportIndexView):
    template_name = "pages/football/index.html"

    def get(self, request, *args, **kwargs):
        leagues = self._prefetch_leagues(
            queryset=football_models.League.objects, kind_of_sport=8
        )

        best_fixture = self._prefetch_best_fixture(
            queryset=football_models.Match.objects, kind_of_sport=8
        )

        kwargs.update(
            best_fixture=best_fixture,
            page_title=_("Volleyball"),
            leagues=leagues,
            type=8,
        )

        return super().get(request=request, *args, **kwargs)


class LazyLoadView(services_prefetch.PrefetchView, views.View):
    template_name = "pages/component/leagues_item.html"

    def get(self, request, *args, **kwargs):
        kind_of_sport = request.GET.get("kind_of_sport")
        page = request.GET.get("page", 1)
        leagues = self._prefetch_leagues(
            queryset=football_models.League.objects, kind_of_sport=kind_of_sport
        )
        paginator = django_paginator.Paginator(object_list=leagues, per_page=4)

        try:
            paginated_leagues = paginator.page(page)
        except django_paginator.EmptyPage:
            return JsonResponse(data={"detail": "Not Found"}, status=404)

        leagues_html = loader.render_to_string(
            context={"leagues": paginated_leagues}, template_name=self.template_name
        )

        output_data = {"posts_html": leagues_html}
        return JsonResponse(output_data)
