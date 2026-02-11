# region				-----External Imports-----
from django.db import models as django_models
from django.utils.html import mark_safe

from bets.models import Event

# region				-----Internal Imports-----
from . import choices as football_choices

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class League(django_models.Model):
    # region           -----Information-----
    kind_of_sport = django_models.PositiveSmallIntegerField(
        choices=football_choices.kinds_of_sport,
        verbose_name="Вид спорту",
        blank=False,
        null=False,
        default=1,
    )

    api_id = django_models.PositiveIntegerField(
        verbose_name="Rapid api id", blank=False, null=True
    )

    title = django_models.CharField(
        verbose_name="League name", max_length=50, blank=False, null=False
    )

    logo = django_models.URLField(verbose_name="League logo", blank=True, null=True)

    flag = django_models.URLField(verbose_name="League flag", blank=True, null=True)

    season = django_models.CharField(
        verbose_name="League season", max_length=250, blank=False, null=False
    )

    round = django_models.CharField(
        verbose_name="League round", max_length=50, blank=False, null=False
    )
    # endregion

    # region           -----Relation-----
    country = django_models.ForeignKey(
        verbose_name="League country",
        on_delete=django_models.SET_NULL,
        blank=False,
        null=True,
        to="geo.Country",
    )

    # endregion

    # region              -----Metas-----
    class Meta(object):
        unique_together = ("id", "api_id")
        verbose_name_plural = "Leagues"
        verbose_name = "League"

    # endregion

    # region         -----Default Methods-----
    def __str__(self) -> str:
        return self.title

    # endregion

    # region         -----Additional Methods-----
    def logo_tag(self) -> str:
        return mark_safe(f"<img src='{self.logo}' width='50' height='50' />")

    logo_tag.short_description = "Logo"
    logo_tag.allow_tags = True
    # endregion


class Match(Event):
    # region           -----Information-----
    api_id = django_models.PositiveIntegerField(
        verbose_name="Rapid api id", blank=False, null=True
    )

    date = django_models.DateTimeField(
        verbose_name="Match date and time", blank=False, null=False
    )

    referee = django_models.CharField(
        verbose_name="Match referee", max_length=100, blank=True, null=True
    )
    # endregion

    # region           -----Relation-----
    home_team = django_models.ForeignKey(
        on_delete=django_models.CASCADE,
        related_name="home_matches",
        verbose_name="Home team",
        blank=False,
        null=False,
        to="Team",
    )

    away_team = django_models.ForeignKey(
        on_delete=django_models.SET_NULL,
        related_name="away_matches",
        verbose_name="Away team",
        blank=False,
        null=True,
        to="Team",
    )

    league = django_models.ForeignKey(
        on_delete=django_models.CASCADE,
        verbose_name="Match league",
        related_name="matches",
        blank=False,
        null=False,
        to="League",
    )

    winer = django_models.ForeignKey(
        on_delete=django_models.CASCADE,
        verbose_name="Match winer",
        related_name="won_matches",
        blank=True,
        null=True,
        to="Team",
    )
    # endregion

    # region              -----Metas-----
    class Meta(object):
        verbose_name_plural = "Matches"
        verbose_name = "Match"

    # endregion

    # region         -----Default Methods-----
    def __str__(self) -> str:
        return f"{self.pk} {self.date}"


# endregion


class Team(django_models.Model):
    # region           -----Information-----
    title = django_models.CharField(
        verbose_name="Team name", max_length=100, blank=False, null=False
    )

    logo = django_models.URLField(verbose_name="Team logo", blank=True, null=True)

    # endregion

    # region              -----Metas-----
    class Meta(object):
        verbose_name_plural = "Teams"
        verbose_name = "Team"

    # endregion

    # region         -----Default Methods-----
    def __str__(self) -> str:
        return f"{self.title}"

    # endregion

    # region         -----Additional Methods-----
    def logo_tag(self) -> str:
        return mark_safe(f"<img src='{self.logo}' width='50' height='50' />")

    logo_tag.short_description = "Logo"
    logo_tag.allow_tags = True


# endregion
