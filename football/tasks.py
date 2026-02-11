import datetime
import logging

# region				-----External Imports-----
import celery

from football.models import League, Match, Team

# region				-----Internal Imports-----
from football.services.rapid import RapidClient
from geo.models import Country

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


logger = logging.Logger(__file__)


@celery.shared_task(name="start_import")
def start_import():
    rapid = RapidClient()
    fixtures = rapid.fetch_fixtures()
    passed = 0
    imported = 0

    for fixture in fixtures:
        match_data = fixture["fixture"]
        league_data = fixture["league"]
        home_team_data = fixture["teams"]["home"]
        away_team_data = fixture["teams"]["away"]

        country, created = Country.objects.get_or_create(title=league_data["country"])

        try:
            league = League.objects.get(id=league_data["id"])
            league.title = league_data["name"]
            league.logo = league_data["logo"]
            league.flag = league_data["flag"]
            league.season = league_data["season"]
            league.round = league_data["season"]
            league.country = country
            league.save()
        except League.DoesNotExist:
            league = League.objects.create(
                id=league_data["id"],
                title=league_data["name"],
                logo=league_data["logo"],
                flag=league_data["flag"],
                season=league_data["season"],
                round=league_data["season"],
                country=country,
            )

        try:
            home_team = Team.objects.get(id=home_team_data["id"])
            if (
                not home_team.logo == home_team_data["logo"]
                or not home_team.title == home_team_data["name"]
            ):
                home_team.logo = home_team_data["logo"]
                home_team.title = home_team_data["name"]
                home_team.save()
        except Team.DoesNotExist:
            home_team = Team.objects.create(
                id=home_team_data["id"],
                logo=home_team_data["logo"],
                title=home_team_data["name"],
            )

        try:
            away_team = Team.objects.get(id=away_team_data["id"])
            if (
                not away_team.logo == away_team_data["logo"]
                or not away_team.title == away_team_data["name"]
            ):
                away_team.logo = away_team_data["logo"]
                away_team.title = away_team_data["name"]
                away_team.save()
        except Team.DoesNotExist:
            away_team = Team.objects.create(
                id=away_team_data["id"],
                logo=away_team_data["logo"],
                title=away_team_data["name"],
            )

        winer = (
            home_team
            if home_team_data["winner"] == True
            else away_team
            if away_team_data["winner"] == True
            else None
        )

        try:
            Match.objects.get(id=match_data["id"])
            passed += 1
        except Match.DoesNotExist:
            Match.objects.create(
                id=match_data["id"],
                referee=match_data["referee"],
                league=league,
                home_team=home_team,
                away_team=away_team,
                winer=winer,
                date=datetime.datetime.strptime(
                    match_data["date"], "%Y-%m-%dT%H:%M:%S%z"
                ),
            )
            imported += 1

    print(f"Imported {imported}, passed {passed}")
