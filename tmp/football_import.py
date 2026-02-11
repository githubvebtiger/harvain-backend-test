from datetime import datetime

from football.models import League, Match, Team
from football.services.rapid import RapidClient
from geo.models import Country

rapid = RapidClient()


def start_import():
    fixtures = rapid.fetch_fixtures()

    for fixture in fixtures:
        match_data = fixture["fixture"]
        league_data = fixture["league"]
        home_team_data = fixture["teams"]["home"]
        away_team_data = fixture["teams"]["away"]

        country, created = Country.objects.get_or_create(title=league_data["country"])

        league, created = League.objects.get_or_create(
            id=league_data["id"],
            title=league_data["name"],
            logo=league_data["logo"],
            flag=league_data["flag"],
            season=league_data["season"],
            round=league_data["season"],
            country=country,
        )

        home_team, created = Team.objects.get_or_create(
            id=home_team_data["id"],
            logo=home_team_data["logo"],
            title=home_team_data["name"],
        )

        away_team, create = Team.objects.get_or_create(
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

        Match.objects.get_or_create(
            id=match_data["id"],
            referee=match_data["referee"],
            league=league,
            home_team=home_team,
            away_team=away_team,
            winer=winer,
            date=datetime.strptime(match_data["date"], "%Y-%m-%dT%H:%M:%S%z"),
        )


def main():
    start_import()
