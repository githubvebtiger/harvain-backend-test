import datetime
import logging
import time

import celery
from django import utils as django_utils

from football import models as football_models
from rapid_api.api import RapidAPI

# region				-----External Imports-----
from utils.dottedpath import dottedpath as utils_dottedpath

# region				-----Internal Imports-----
from . import services as bet_services

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


logger = logging.Logger(__file__)


@celery.shared_task(name="task_volleyball_data_import")
def task_volleyball_data_import():
    host = "api-volleyball.p.rapidapi.com"
    version = None
    rapid = RapidAPI(host=host, version=version, path="games")
    data = django_utils.timezone.now()

    datas = [data, data + datetime.timedelta(days=1)]

    for data in datas:
        fixtures = rapid.fetch_data(search_by={"date": data.strftime("%Y-%m-%d")})
        for fixture in fixtures:
            try:
                home_team_data = utils_dottedpath(data=fixture, path="teams.home")
                away_team_data = utils_dottedpath(data=fixture, path="teams.away")
                country_data = utils_dottedpath(data=fixture, path="country")
                league_data = utils_dottedpath(data=fixture, path="league")

                country = bet_services.create_or_get_country(data=country_data)

                league = bet_services.create_or_get_league(
                    kind_of_sport=8, data=league_data, country=country, version=version
                )

                home_team = bet_services.create_or_get_team(data=home_team_data)

                away_team = bet_services.create_or_get_team(data=away_team_data)

                winner = bet_services.find_winner(
                    home_team=home_team,
                    away_team=away_team,
                    fixture=fixture,
                    version=version,
                )

                football_models.Match.objects.update_or_create(
                    api_id=int(utils_dottedpath(data=fixture, path="id")),
                    league=league,
                    defaults={
                        "api_id": int(utils_dottedpath(data=fixture, path="id")),
                        "date": datetime.datetime.strptime(
                            utils_dottedpath(data=fixture, path="date"),
                            "%Y-%m-%dT%H:%M:%S%z",
                        ),
                        "home_team": home_team,
                        "away_team": away_team,
                        "league": league,
                        "winer": winner,
                    },
                )
            except Exception as ex:
                logger.error(ex)
        events_id = list(
            map(lambda fixture: utils_dottedpath(data=fixture, path="id"), fixtures)
        )

        logger.info(f"king of sport 8")
        logger.info(f"fixtures {len(events_id)}")

        bet_services.generate_odds(events_id=events_id, version=version, host=host)
        bet_services.create_cache(kind_of_sport=8)
