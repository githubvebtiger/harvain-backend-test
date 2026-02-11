import logging

# region				-----External Imports-----
import celery
from django import utils

# region				-----Internal Imports-----
from .models import Satellite

# endregion

# endregion

# region			  -----Supporting Variables-----
logger = logging.getLogger(__name__)
# endregion


@celery.shared_task(name="task_satellites_balance_migrating", soft_time_limit=300, time_limit=600)
def task_satellites_balance_migrating(*args, **kwargs) -> None:
    satellites_query = Satellite.objects.filter(system=True).filter(satellite_client__isnull=False)

    for satellite in satellites_query:
        last_migration_time = satellite.migration_time
        interval = satellite.interval

        second_migration_time = satellite.second_migration_time
        second_interval = satellite.second_interval
        current_time = utils.timezone.now()

        logger.info(f"Migrating satellite with UUID: {satellite.uuid}")

        if not second_interval and interval:
            satellite.second_interval = interval
            satellite.second_migration_time = utils.timezone.now()
            satellite.save()

            second_migration_time = satellite.second_migration_time
            second_interval = satellite.second_interval

        if second_interval and current_time >= second_migration_time + second_interval:
            if satellite.active_balance:
                satellite.withdrawal = (
                    satellite.active_balance
                    if not satellite.withdrawal
                    else satellite.active_balance + satellite.withdrawal
                )
                satellite.active_balance = 0
            satellite.second_migration_time = utils.timezone.now()
            satellite.save()

        if interval and current_time >= last_migration_time + interval:
            if satellite.block_balance:
                satellite.active_balance = (
                    satellite.block_balance
                    if not satellite.active_balance
                    else satellite.block_balance + satellite.active_balance
                )
                satellite.block_balance = 0
            satellite.migration_time = utils.timezone.now()
            satellite.save()
