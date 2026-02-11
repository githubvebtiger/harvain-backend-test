import copy

# region				-----External Imports-----
import logging
import typing

from django import dispatch
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models as django_models

import utils
from football import models as football_models
from geo import models as geo_models
from history.middleware import get_current_user
from history.models import HistoryLog
from integrations import google

from ... import models

# endregion

# region				-----Internal Imports-----
logger = logging.Logger(__file__)
# endregion


@dispatch.receiver(signal=django_models.signals.pre_save, sender=models.OddsDetail)
def translate_odd_details(instance: typing.Any, raw: bool = True, *args, **kwargs) -> None:
    if raw:  # if data saves from loaddata
        return
    try:
        instance = utils.translate.multiple_translations(instance=instance)
    except:
        pass


@dispatch.receiver(signal=django_models.signals.pre_save, sender=models.Odds)
def translate_odd(instance: typing.Any, raw: bool = True, *args, **kwargs) -> None:
    if raw:  # if data saves from loaddata
        return
    try:
        instance = utils.translate.multiple_translations(instance=instance)
    except:
        pass


@dispatch.receiver(signal=django_models.signals.pre_save, sender=models.Bet)
def change_bet(instance: typing.Any, raw: bool = True, *args, **kwargs) -> None:
    if raw:  # if data saves from loaddata
        return
    
    if instance.pk:
        try:

            current_user = get_current_user()
            if not current_user or str(current_user) == "AnonymousUser":
                raise ObjectDoesNotExist

            bet_before = models.Bet.objects.get(pk=instance.pk)
            changes = []

            if instance.status != bet_before.status:
                changes.append(f"status changed {bet_before.status} -> {instance.status}")

            if instance.type != bet_before.type:
                changes.append(f"type (Single/Any) changed {bet_before.type} -> {instance.type}")

            if instance.date_of_game != bet_before.date_of_game:
                changes.append(f"date of game changed {bet_before.date_of_game} -> {instance.date_of_game}")

            if instance.created_at != bet_before.created_at:
                changes.append(f"created at changed {bet_before.created_at} -> {instance.created_at}")

            if instance.game_score != bet_before.game_score:
                changes.append(f"game score changed {bet_before.game_score} -> {instance.game_score}")

            if instance.number != bet_before.number:
                changes.append(f"number changed {bet_before.number} -> {instance.number}")

            if instance.commision != bet_before.commision:
                changes.append(f"commision changed {bet_before.commision} -> {instance.commision}")

            if instance.commands != bet_before.commands:
                changes.append(f"commands changed {bet_before.commands} -> {instance.commands}")

            if instance.event_id != bet_before.event_id:
                changes.append(f"event_id changed {bet_before.event_id} -> {instance.event_id}")

            if instance.country != bet_before.country:
                changes.append(f"country changed {bet_before.country} -> {instance.country}")

            if instance.result != bet_before.result:
                changes.append(f"result changed {bet_before.result} -> {instance.result}")

            if instance.rate != bet_before.rate:
                changes.append(f"rate changed {bet_before.rate} -> {instance.rate}")

            if instance.stake != bet_before.stake:
                changes.append(f"stake changed {bet_before.stake} -> {instance.stake}")

            if instance.sport != bet_before.sport:
                changes.append(f"sport changed {bet_before.sport} -> {instance.sport}")

            if instance.event != bet_before.event:
                changes.append(f"bet type changed {bet_before.event} -> {instance.event}")

            if instance.odds_value != bet_before.odds_value:
                changes.append(f"odds value (КЕФ) changed {bet_before.odds_value} -> {instance.odds_value}")

            if instance.on != bet_before.on:
                changes.append(f"score target changed {bet_before.on} -> {instance.on}")

            if changes:
                HistoryLog.objects.create(
                    type="bet result change",
                    change_message=f"bet {instance.pk}:\n" + ",\n".join(changes),
                    user=current_user,
                    client=instance.client.full_name,
                    salesman=instance.client.salesman,
                )
        except ObjectDoesNotExist:
            pass
