# region				-----External Imports-----
from django import http, shortcuts, views

from football.services.sportingnews import SportingNewsClient
from user.mixins import SatelliteRequiredMixin

# region				-----Internal Imports-----
from .models import Transaction

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class TransactionsRefillView(SatelliteRequiredMixin, views.View):
    def get(self, request, *args, **kwargs) -> http.request.HttpRequest:
        transactions = (
            Transaction.objects.filter(
                client_id=request.user.satellite.satellite_client.pk
            )
            .filter(type=1)
            .all()
        )

        rss_news = SportingNewsClient().rss_list()

        return shortcuts.render(
            request=request,
            template_name="pages/transactions/index.html",
            context={"transactions": transactions, "rss_news": rss_news},
        )


class TransactionsWithdrawView(SatelliteRequiredMixin, views.View):
    def get(self, request, *args, **kwargs) -> http.request.HttpRequest:
        transactions = (
            Transaction.objects.filter(
                client_id=request.user.satellite.satellite_client.pk
            )
            .filter(type=2)
            .all()
        )

        rss_news = SportingNewsClient().rss_list()

        return shortcuts.render(
            request=request,
            template_name="pages/transactions/index.html",
            context={"transactions": transactions, "rss_news": rss_news},
        )
