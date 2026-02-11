import typing

from django import http, shortcuts, views
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models

from bets import models as bets_models
from football.services import prefetch as services_prefetch
from football.services.sportingnews import SportingNewsClient

from ..client.models import Client
from . import forms
from .models import Satellite


class SatellitesView(LoginRequiredMixin, services_prefetch.SportIndexView, views.View):
    def get(self, request, *args, **kwargs) -> http.request.HttpRequest:
        try:
            if request.user.satellite:
                return shortcuts.redirect("bets-wins")
        except Satellite.DoesNotExist:
            pass

        satellites: typing.List[Satellite] = []

        try:
            satellites_list = list(
                Satellite.objects.filter(satellite_client=request.user.client)
                .order_by(models.F("order").asc(nulls_first=True))
                .values(
                    "uuid", "order", "block_balance", "active_balance", "withdrawal"
                )
            )
            satellites_count = Satellite.objects.filter(
                satellite_client=request.user.client
            ).count()
        except Client.DoesNotExist:
            logout(request=request)
            return shortcuts.redirect("football-index")

        # ordering
        for satellite_index in range(satellites_count):
            # find satellite index or -1
            satellite_index = next(
                (
                    i
                    for i, satellite in enumerate(satellites_list)
                    if satellite["order"] == satellite_index + 1
                ),
                -1,
            )

            if satellite_index == -1:
                satellites.append(satellites_list[0])
                del satellites_list[0]
            else:
                satellites.append(satellites_list[satellite_index])
                del satellites_list[satellite_index]

        rss_news = SportingNewsClient().rss_list()
        sports_amount = self._count_fixtures(queryset=bets_models.Odds.objects)

        return shortcuts.render(
            request=request,
            template_name="pages/satellites.html",
            context={
                "satellites": satellites,
                "sports_amount": sports_amount,
                "rss_news": rss_news,
            },
        )


class LoginView(views.View):
    def post(self, request, *args, **kwargs):
        form = forms.SatelliteLoginForm(request.POST)
        if not form.is_valid():
            return http.JsonResponse(
                {"message": "No account with credentials"}, status=400
            )

        user = authenticate(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if not user:
            return http.JsonResponse(
                {"message": "No account with credentials"}, status=400
            )

        try:
            satellite = user.satellite
            if not satellite.allow_auth:
                raise Satellite.DoesNotExist

            if satellite.blocked:
                return http.JsonResponse(
                    {
                        "message": satellite.message_for_blocked,
                        "blocked": True,
                    },
                    status=401,
                )
        except Satellite.DoesNotExist:
            return http.JsonResponse(
                {"message": "No account with credentials"}, status=400
            )

        login(request, user)

        return http.JsonResponse({"message": "Success"}, status=200)


class SignUpView(services_prefetch.SportIndexView):
    def get(self, request, *args, **kwargs) -> http.request.HttpRequest:
        sports_amount = self._count_fixtures(queryset=bets_models.Odds.objects)
        return shortcuts.render(
            request=request,
            template_name="signup.html",
            context={
                "sports_amount": sports_amount,
            },
        )
