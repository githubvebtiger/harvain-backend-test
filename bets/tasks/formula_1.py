import datetime
import logging
import time

import celery
from django import utils as django_utils

from football import models as football_models
from geo import models as geo_models
from rapid_api.api import RapidAPI

# region				-----External Imports-----
from utils.dottedpath import dottedpath as utils_dottedpath

# endregion

# region				-----Internal Imports-----
# endregion

# region			  -----Supporting Variables-----
# endregion


logger = logging.Logger(__file__)


@celery.shared_task(name="task_formula_1_data_import")
def task_formula_1_data_import():
    host = "api-formula-1.p.rapidapi.com"
    version = None
    rapid = RapidAPI(host=host, version=version, path="races")
    data = django_utils.timezone.now()

    datas = [data, data + datetime.timedelta(days=1)]

    for data in datas:
        fixtures = rapid.fetch_data(search_by={"date": data.strftime("%Y-%m-%d")})
        for index, fixture in enumerate(fixtures, 1):
            try:
                country_data = utils_dottedpath(
                    data=fixture, path="competition.location"
                )

                country, _ = geo_models.Country.objects.update_or_create(
                    title=utils_dottedpath(data=country_data, path="country")
                )

                league, _ = football_models.League.objects.update_or_create(
                    api_id=int(utils_dottedpath(data=fixture, path="competition.id")),
                    defaults={
                        "season": utils_dottedpath(data=fixture, path="season"),
                        "title": utils_dottedpath(
                            data=fixture, path="competition.name"
                        ),
                        "api_id": int(
                            utils_dottedpath(data=fixture, path="competition.id")
                        ),
                        "kind_of_sport": 4,
                        "country": country,
                    },
                )

                driver_rapid = RapidAPI(host=host, version=version, path="drivers")
                driver_response = driver_rapid.fetch_data(
                    search_by={
                        "id": utils_dottedpath(
                            path="fastest_lap.driver.id", data=fixture
                        )
                    }
                )

                home_team, _ = football_models.Team.objects.update_or_create(
                    title=utils_dottedpath(data=driver_response, path="name")
                )

                football_models.Match.objects.update_or_create(
                    api_id=int(utils_dottedpath(data=fixture, path="id")),
                    defaults={
                        "api_id": int(utils_dottedpath(data=fixture, path="id")),
                        "date": datetime.datetime.strptime(
                            utils_dottedpath(data=fixture, path="date"),
                            "%Y-%m-%dT%H:%M:%S%z",
                        ),
                        "home_team": home_team,
                        "league": league,
                    },
                )
            except Exception as ex:
                logger.error(ex)
            finally:
                if index % 100 == 0:
                    time.sleep(60)

        logger.info(f"king of sport 4")
        bet_services.create_cache(kind_of_sport=4)
