# region				-----External Imports-----
from django import utils
from django.db import models as django_models
from django.utils.translation import gettext_lazy as _

from football import models as football_models

# region				-----Internal Imports-----
from . import choices

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class Event(django_models.Model):
    pass


class Trade(django_models.Model):
    opened = django_models.DateTimeField(null=True, blank=True)
    closed = django_models.DateTimeField(null=True, blank=True)
    traiding_pair = django_models.CharField(max_length=255)
    tp_sl = django_models.CharField(max_length=255)
    deposit = django_models.CharField(max_length=255)
    closing_pnl = django_models.CharField(_("Closed P&L (USDT)"), max_length=255)
    exchange = django_models.CharField(max_length=255)
    direction = django_models.CharField(max_length=255)
    orders_type = django_models.CharField(max_length=255)
    fee = django_models.CharField(_("Commission"), max_length=255)
    closing_fee = django_models.CharField(max_length=255, null=True, blank=True)
    opening_fee = django_models.CharField(max_length=255, null=True, blank=True)
    client = django_models.ForeignKey(
        on_delete=django_models.CASCADE,
        verbose_name="Клієнт",
        related_name="trades",
        to="user.Client",
        blank=False,
        null=False,
    )


class Bet(django_models.Model):

    # region           -----Information-----
    status = django_models.PositiveSmallIntegerField(
        choices=choices.statuses,
        verbose_name="Статус",
        blank=False,
        null=False,
        default=1,
    )

    type = django_models.PositiveSmallIntegerField(
        choices=choices.types, verbose_name="Тип", blank=False, null=False, default=1
    )

    date_of_game = django_models.CharField(verbose_name="Час та дата матчу", max_length=1000, blank=False, default="")

    created_at = django_models.CharField(
        verbose_name="Час та дата створення ставки",
        max_length=1000,
        blank=False,
        default="",
    )

    game_score = django_models.CharField(verbose_name="Рахунок гри", max_length=1000, blank=False, default="")

    number = django_models.CharField(verbose_name="Номер ставки", max_length=1000, blank=False, default="")

    commision = django_models.FloatField(verbose_name="Комісія (сума)", blank=True, null=True)

    commands = django_models.CharField(verbose_name="Команди", max_length=1000, blank=False, default="")

    event_id = django_models.CharField(verbose_name="Event ID", max_length=7, blank=False, default="")

    country = django_models.CharField(verbose_name="Країна", max_length=1000, blank=False, default="")

    result = django_models.FloatField(verbose_name="Виграш", blank=True, null=True)

    league = django_models.CharField(verbose_name="Ліга", max_length=1000, blank=False, default="")

    rate = django_models.CharField(verbose_name="Bet rate", max_length=50, blank=False, null=False)

    stake = django_models.FloatField(verbose_name="Сума ставки", blank=False, null=False)

    sport = django_models.TextField(verbose_name="Спорт", max_length=1000, blank=False, default="")

    event = django_models.CharField(
        verbose_name="Тип ставки (точний рахунок, результат тощо)",
        max_length=1000,
        blank=False,
        default="",
    )

    odds_value = django_models.FloatField(verbose_name="КЕФ", blank=False, null=False, default=0)

    on = django_models.CharField(verbose_name="На який рахунок ставили", max_length=50, blank=False, null=False)
    # endregion

    # region           -----Relation-----
    client = django_models.ForeignKey(
        on_delete=django_models.CASCADE,
        verbose_name="Клієнт",
        related_name="bets",
        to="user.Client",
        blank=False,
        null=False,
    )

    odds = django_models.ForeignKey(
        on_delete=django_models.CASCADE,
        related_name="bets",
        verbose_name="Odds",
        to="bets.Odds",
        blank=True,
        null=True,
    )

    # endregion

    # region              -----Metas-----
    class Meta(object):
        verbose_name_plural = "Ставки"
        verbose_name = "Ставка"

    # endregion

    # region         -----Default Methods-----
    def __str__(self) -> str:
        return f"{self.id} {self.created_at}"

    def result_abs(self) -> float:
        return abs(self.result) if not self.result == None else None

    # endregion


class Odds(django_models.Model):
    # region           -----Relation-----
    fixture = django_models.ForeignKey(
        on_delete=django_models.CASCADE,
        verbose_name="Подія",
        related_name="odds",
        to="football.Match",
        blank=False,
        null=True,
    )
    # endregion

    # region           -----Information-----
    name = django_models.CharField(verbose_name="Назва", max_length=255, blank=False, null=False)
    # endregion

    # region              -----Metas-----
    class Meta(object):
        unique_together = ("name", "fixture")

    # endregion

    # region         -----Default Methods-----
    def __str__(self) -> str:
        return f"{self.name} ID: {self.id}"

    # endregion


class OddsDetail(django_models.Model):
    # region           -----Relation-----
    odds = django_models.ForeignKey(
        on_delete=django_models.CASCADE,
        related_name="odds_detail",
        verbose_name="Odds",
        to="bets.Odds",
        blank=False,
        null=False,
    )
    # endregion

    # region           -----Information-----
    value = django_models.DecimalField(verbose_name="Значення", decimal_places=2, max_digits=100, default=0)

    name = django_models.CharField(verbose_name="Назва", max_length=255, blank=False, null=False)
    # endregion

    # region         -----Default Methods-----
    def __str__(self) -> str:
        return f"{self.name} ID: {self.id}"

    # endregion
