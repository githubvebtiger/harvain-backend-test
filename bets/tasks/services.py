import logging
import random
import time
import typing
from datetime import datetime

import requests
from django.urls import reverse

from football import models as football_models
from football.services import rapid as football_types
from geo import models as geo_models
from rapid_api.api import RapidAPI

# region				-----External Imports-----
from utils.dottedpath import dottedpath as utils_dottedpath

# region				-----Internal Imports-----
from .. import models as bets_models

# endregion

# endregion

# region			  -----Supporting Variables-----
logger = logging.Logger(__file__)
# endregion


def create_or_get_team(data: football_types.TeamValueType) -> football_models.Team:
    team, _ = football_models.Team.objects.update_or_create(
        id=int(utils_dottedpath(data=data, path="id")),
        defaults={
            "title": utils_dottedpath(data=data, path="name"),
            "logo": utils_dottedpath(data=data, path="logo"),
            "id": int(utils_dottedpath(data=data, path="id")),
        },
    )

    return team


def create_or_get_country(data: football_types.CountryType) -> geo_models.Country:
    country, _ = geo_models.Country.objects.update_or_create(
        title=utils_dottedpath(data=data, path="name")
    )
    return country


def create_or_get_league(
    data: football_types.LeagueType,
    country: geo_models.Country,
    version: str or None,
    kind_of_sport: int,
) -> football_models.League:
    defaults = {
        "season": str(utils_dottedpath(data=data, path="season")),
        "title": utils_dottedpath(data=data, path="name"),
        "api_id": int(utils_dottedpath(data=data, path="id")),
        "logo": utils_dottedpath(data=data, path="logo"),
        "kind_of_sport": kind_of_sport,
        "country": country,
    }
    if version:
        defaults.update(
            round=str(utils_dottedpath(data=data, path="season")),
            flag=utils_dottedpath(data=data, path="flag"),
        )

    league, _ = football_models.League.objects.update_or_create(
        api_id=utils_dottedpath(data=data, path="id"),
        kind_of_sport=kind_of_sport,
        defaults=defaults,
    )
    return league


def generate_odds(events_id: typing.List[id], version: str or None, host: str) -> None:
    for index_event_id, event_id in enumerate(events_id, 1):
        rapid = RapidAPI(version=version, path="odds", host=host)
        params = {"fixture": event_id} if version else {"game": event_id}
        response = rapid.fetch_data(search_by=params)
        if index_event_id % 100 == 0:
            time.sleep(60)
        try:
            for odds in response:
                fixture_id_path = "fixture.id" if version else "game.id"
                fixture_id = utils_dottedpath(data=odds, path=fixture_id_path)
                bookmakers = utils_dottedpath(data=odds, path="bookmakers")
                best_bookmakers = bookmakers[max(map(len, bookmakers))]

                bets = utils_dottedpath(data=best_bookmakers, path="bets")
                if bets and not any(
                    elem.get("name") == "Match Winner" for elem in bets
                ):
                    odds = bets_models.Odds.objects.create(
                        name="Match Winner",
                        fixture=football_models.Match.objects.get(api_id=fixture_id),
                    )
                    for name in ["Home", "Away"]:
                        bets_models.OddsDetail.objects.create(
                            value=get_random_odd(), name=name, odds=odds
                        )

                for index_bet, bet in enumerate(bets, 1):
                    odds = bets_models.Odds.objects.create(
                        name=utils_dottedpath(data=bet, path="name"),
                        fixture=football_models.Match.objects.get(api_id=fixture_id),
                    )

                    odds_details = utils_dottedpath(data=bet, path="values")
                    for index_odds_detail, odds_detail in enumerate(odds_details, 1):
                        bets_models.OddsDetail.objects.create(
                            value=float(odds_detail.get("odd")),
                            name=odds_detail.get("value"),
                            odds=odds,
                        )
                        if index_odds_detail >= 4:
                            logger.info(f"odds detail 4")
                            break

                    if index_bet >= 6:
                        logger.info(f"odds 6")
                        break
        except Exception as ex:
            logger.error(ex)


def get_random_odd() -> float:
    return round(random.uniform(1, 5), 2)


def find_winner(
    home_team: football_models.Team,
    away_team: football_models.Team,
    version: str or None,
    fixture: dict,
) -> football_models.Team or None:
    home_data = utils_dottedpath(data=fixture, path="teams.home")
    away_data = utils_dottedpath(data=fixture, path="teams.away")
    if version:
        winner = (
            home_team
            if home_data["winner"]
            else away_team if away_data["winner"] else None
        )
    else:
        home_score = utils_dottedpath(data=fixture, path="scores.home")
        away_score = utils_dottedpath(data=fixture, path="scores.away")
        if isinstance(home_score, dict):
            home_score = utils_dottedpath(data=home_score, path="total")
            away_score = utils_dottedpath(data=away_score, path="total")

        if not home_score or not away_score:
            return None

        winner = (
            home_team
            if home_score > away_score
            else away_team
            if home_score < away_score
            else None
        )
    return winner


def create_cache(kind_of_sport: int):
    t = int(datetime.datetime.now().timestamp() * 1000)
    requests.get(
        "https://admin.greekz.com"
        + reverse("frontend-league-list")
        + f"?kind_of_sport={kind_of_sport}&page_size=10&page=1&t={t}&cache=True",
    )
