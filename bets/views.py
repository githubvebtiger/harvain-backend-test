# region				-----External Imports-----
from django import http, shortcuts, views

from football.services import prefetch as services_prefetch
from football.services.sportingnews import SportingNewsClient
from user.mixins import SatelliteRequiredMixin

# region				-----Internal Imports-----
from .models import Bet, Odds

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class BetsWinsView(
    SatelliteRequiredMixin, services_prefetch.SportIndexView, views.View
):
    def get(self, request, *args, **kwargs) -> http.request.HttpRequest:
        bets = (
            Bet.objects.select_related("client")
            .filter(client_id=request.user.satellite.satellite_client.pk)
            .filter(result__gte=0)
            .all()
        )

        rss_news = SportingNewsClient().rss_list()
        sports_amount = self._count_fixtures(queryset=Odds.objects)

        return shortcuts.render(
            request=request,
            template_name="pages/bets/index.html",
            context={
                "bets": bets,
                "sports_amount": sports_amount,
                "rss_news": rss_news,
            },
        )


class BetsLossesView(
    SatelliteRequiredMixin, services_prefetch.SportIndexView, views.View
):
    def get(self, request, *args, **kwargs) -> http.request.HttpRequest:
        bets = (
            Bet.objects.select_related("client")
            .filter(client_id=request.user.satellite.satellite_client.pk)
            .filter(result__lte=0)
            .all()
        )

        rss_news = SportingNewsClient().rss_list()
        sports_amount = self._count_fixtures(queryset=Odds.objects)

        return shortcuts.render(
            request=request,
            template_name="pages/bets/index.html",
            context={
                "bets": bets,
                "sports_amount": sports_amount,
                "rss_news": rss_news,
            },
        )


class BetsProgressView(
    SatelliteRequiredMixin, services_prefetch.SportIndexView, views.View
):
    def get(self, request, *args, **kwargs) -> http.request.HttpRequest:
        bets = (
            Bet.objects.select_related("client")
            .filter(client_id=request.user.satellite.satellite_client.pk)
            .filter(status=1)
            .all()
        )

        rss_news = SportingNewsClient().rss_list()
        sports_amount = self._count_fixtures(queryset=Odds.objects)

        return shortcuts.render(
            request=request,
            template_name="pages/bets/index.html",
            context={
                "bets": bets,
                "sports_amount": sports_amount,
                "rss_news": rss_news,
            },
        )


class NewsView(services_prefetch.SportIndexView):
    template_name = "pages/news/index.html"

    def get(self, request, *args, **kwargs) -> http.request.HttpRequest:
        rss_news = SportingNewsClient().rss_list()
        sports_amount = self._count_fixtures(queryset=Odds.objects)

        return shortcuts.render(
            request=request,
            template_name="pages/news/index.html",
            context={"sports_amount": sports_amount, "rss_news": rss_news},
        )
