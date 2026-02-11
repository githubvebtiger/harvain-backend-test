import datetime
import typing

import requests

# region				-----External Imports-----
from django import conf, utils

# region				-----Internal Imports-----
from .exceptions import RapidException

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class OddType(typing.TypedDict):
    odd: str  # float in string
    value: str


class CountryType(typing.TypedDict):
    title: str


class BetType(typing.TypedDict):
    id: int
    name: str
    values: typing.List[OddType]


class BookmakerType(typing.TypedDict):
    id: int
    name: str
    bets: typing.List[BetType]


class OddsResponseType(typing.TypedDict):
    bookmakers: typing.List[BookmakerType]


class FixtureType(typing.TypedDict):
    id: int
    referee: str
    date: str


class LeagueType(typing.TypedDict):
    id: int
    name: str
    country: str
    flag: str
    logo: str
    round: str
    season: int


class TeamValueType(typing.TypedDict):
    id: int
    logo: str
    name: str
    winner: bool


class TeamType(typing.TypedDict):
    away: TeamValueType
    home: TeamValueType


class FixturesResponseType(typing.TypedDict):
    fixture: FixtureType
    league: LeagueType
    teams: TeamType


class RapidClient:
    def __init__(self) -> None:
        self._host = conf.settings.RAPID_API_HOST
        self._key = conf.settings.RAPID_API_KEY
        self._version = "v3"

        self._fixtures_path = "fixtures"
        self._odds_path = "odds"

    @property
    def fixtures_url(self) -> str:
        return f"https://{self._host}/{self._version}/{self._fixtures_path}"

    @property
    def odds_url(self) -> str:
        return f"https://{self._host}/{self._version}/{self._odds_path}"

    def _request_headers(self) -> typing.Dict:
        return {"X-RapidAPI-Host": self._host, "X-RapidAPI-Key": self._key}

    def fetch_fixtures(
        self, date: datetime.datetime = None
    ) -> typing.List[FixturesResponseType]:
        if not date:
            date = utils.timezone.now()

        try:
            return requests.get(
                self.fixtures_url,
                headers=self._request_headers(),
                params={"date": date.strftime("%Y-%m-%d")},
            ).json()["response"]
        except requests.exceptions.RequestException:
            raise RapidException

    def fetch_odds(self, fixture_id: int) -> typing.List[OddsResponseType]:
        try:
            return requests.get(
                self.odds_url,
                headers=self._request_headers(),
                params={"fixture": fixture_id},
            ).json()["response"]
        except requests.exceptions.RequestException:
            raise RapidException
