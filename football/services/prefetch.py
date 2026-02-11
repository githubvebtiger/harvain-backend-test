import datetime
import typing

from django import http, shortcuts, utils, views
from django.conf import settings

# region				-----External Imports-----
from django.core import paginator as django_paginator
from django.db import models as django_models
from django.utils import translation

from bets import models as bets_models
from football import models as football_models

# region				-----Internal Imports-----
from . import best_leagues as services_best_leagues
from . import sportingnews as services_sportingnews

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class PrefetchView(services_best_leagues.BestLeagues):
    def _prefetch_leagues(
        self,
        queryset: django_models.QuerySet[football_models.League],
        kind_of_sport: int,
    ) -> django_models.QuerySet[football_models.League]:
        current_datetime = utils.timezone.now() + datetime.timedelta(hours=2)
        filtered_query = django_models.Q()
        match_filtered_query = django_models.Q()

        if kind_of_sport != 4:
            match_filtered_query = django_models.Q(odds__isnull=False)
            filtered_query &= django_models.Q(matches__odds__isnull=False)

        filter_mathces_counter = django_models.Q(
            matches__date__gte=current_datetime,
            matches__date__hour__gte=current_datetime.hour,
        )

        filter_odds_counter = django_models.Q(
            matches__odds__fixture__date__gte=current_datetime,
            matches__odds__fixture__date__hour__gte=current_datetime.hour,
        )

        filter_matches = django_models.Q(
            date__gte=current_datetime,
            date__hour__gte=current_datetime.hour,
        )

        return (
            queryset.filter(filtered_query, kind_of_sport=kind_of_sport)
            .prefetch_related(
                django_models.Prefetch(
                    queryset=football_models.Match.objects.filter(
                        match_filtered_query, filter_matches
                    )
                    .select_related("home_team")
                    .select_related("away_team")
                    .annotate(
                        main_odds_1=bets_models.Odds.objects.filter(
                            fixture_id=django_models.OuterRef("id")
                        )
                        .filter(django_models.Q(name_en_us="Match Winner"))
                        .values("odds_detail__value")[0:1]
                    )
                    .annotate(
                        main_odds_x=bets_models.Odds.objects.filter(
                            fixture_id=django_models.OuterRef("id")
                        )
                        .filter(django_models.Q(name_en_us="Match Winner"))
                        .values("odds_detail__value")[1:2]
                    )
                    .annotate(
                        main_odds_2=bets_models.Odds.objects.filter(
                            fixture_id=django_models.OuterRef("id")
                        )
                        .filter(django_models.Q(name_en_us="Match Winner"))
                        .values("odds_detail__value")[2:3]
                    )
                    .prefetch_related(
                        django_models.Prefetch(
                            queryset=bets_models.Odds.objects.exclude(
                                django_models.Q(name_en_us="Match Winner")
                            )
                            .prefetch_related("odds_detail")
                            .only("name"),
                            lookup="odds",
                        )
                    )
                    .distinct("id"),
                    lookup="matches",
                )
            )
            .annotate(
                matches_counter=django_models.Count(
                    "matches", filter=filter_mathces_counter
                )
            )
            .annotate(
                odds_counter=django_models.Count(
                    "matches__odds", filter=filter_odds_counter
                )
            )
            .select_related("country")
            .exclude(odds_counter=0)
            .all()
        )

    def _prefetch_best_fixture(
        self,
        queryset: django_models.QuerySet[football_models.Match],
        kind_of_sport: int,
    ) -> football_models.Match:
        current_datetime = utils.timezone.now() + datetime.timedelta(hours=2)
        filtered_query = django_models.Q(
            league__kind_of_sport=kind_of_sport,
            date__month=current_datetime.month,
            date__year=current_datetime.year,
            date__day=current_datetime.day,
        )

        if kind_of_sport != 4:
            filtered_query &= django_models.Q(odds__isnull=False)

        fixture = queryset.filter(
            filtered_query
            & (
                django_models.Q(league__title_en_us__in=str(self.leagues.get(1)))
                | django_models.Q(league__country__title_en_us__in=self.countries)
            )
        )
        if not fixture.exists():
            fixture = queryset.filter(filtered_query)

        return (
            fixture.prefetch_related(
                django_models.Prefetch(
                    queryset=bets_models.Odds.objects.filter(
                        django_models.Q(name_en_us="Match Winner")
                    )
                    .prefetch_related("odds_detail")
                    .only("name"),
                    lookup="odds",
                )
            )
            .select_related("home_team")
            .select_related("away_team")
            .only("home_team", "away_team", "league", "date", "referee")
            .first()
        )

    def _count_fixtures(
        self, queryset: django_models.QuerySet[bets_models.Odds]
    ) -> list:
        current_datetime = utils.timezone.now() + datetime.timedelta(hours=2)
        queryset = (
            queryset.filter(
                fixture__date__gte=current_datetime,
                fixture__date__hour__gte=current_datetime.hour,
            )
            .distinct("fixture__league__kind_of_sport")
            .values_list("fixture__league__kind_of_sport", flat=True)
        )

        return list(queryset)


class SportIndexView(PrefetchView, views.View):
    template_name = None

    def get(self, request: http.HttpRequest, *args, **kwargs):
        best_fixture = kwargs.pop("best_fixture")
        page_title = kwargs.pop("page_title")
        page = request.GET.get("page", 1)
        leagues = kwargs.pop("leagues")
        type = kwargs.pop("type")
        paginator = django_paginator.Paginator(object_list=leagues, per_page=4)
        paginated_leagues = paginator.get_page(page)

        rss_news = services_sportingnews.SportingNewsClient().rss_list()

        sports_amount = self._count_fixtures(queryset=bets_models.Odds.objects)
        context = {
            "sports_amount": sports_amount,
            "best_fixture": best_fixture,
            "leagues": paginated_leagues,
            "page_title": page_title,
            "rss_news": rss_news,
            "type": type,
        }

        return shortcuts.render(
            template_name=self.template_name, request=request, context=context
        )
