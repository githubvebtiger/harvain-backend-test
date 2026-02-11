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


@dispatch.receiver(signal=django_models.signals.pre_save, sender=models.League)
def translate_league(instance: typing.Any, raw: bool = True, *args, **kwargs) -> None:
    if raw:  # if data saves from loaddata
        return
    
    try:
        instance = utils.translate.multiple_translations(instance=instance)
    except:
        pass


@dispatch.receiver(signal=django_models.signals.pre_save, sender=models.Match)
def translate_match(instance: typing.Any, raw: bool = True, *args, **kwargs) -> None:
    if raw:  # if data saves from loaddata
        return
    
    try:
        instance = utils.translate.multiple_translations(instance=instance)
    except:
        pass

    if instance and instance.pk:
        try:

            current_user = get_current_user()
            if not current_user or str(current_user) == "AnonymousUser":
                raise ObjectDoesNotExist

            match_before = models.Match.objects.get(pk=instance.pk)
            changes = []

            if instance.date != match_before.date:
                changes.append(f"date changed {match_before.date} -> {instance.date}")

            if instance.referee != match_before.referee:
                changes.append(f"referee changed {match_before.referee} -> {instance.referee}")

            if instance.home_team != match_before.home_team:
                changes.append(f"home_team changed {match_before.home_team} -> {instance.home_team}")

            if instance.away_team != match_before.away_team:
                changes.append(f"away_team changed {match_before.away_team} -> {instance.away_team}")

            if instance.league != match_before.league:
                changes.append(f"league changed {match_before.league} -> {instance.league}")

            if instance.winer != match_before.winer:
                changes.append(f"winer changed {match_before.winer} -> {instance.winer}")

            if changes:
                HistoryLog.objects.create(
                    type="match change",
                    change_message=f"match {instance.pk}:\n" + ",\n".join(changes),
                    user=current_user,
                )
        except ObjectDoesNotExist:
            pass


@dispatch.receiver(signal=django_models.signals.pre_save, sender=models.Team)
def translate_team(instance: typing.Any, raw: bool = True, *args, **kwargs) -> None:
    if raw:  # if data saves from loaddata
        return
    
    try:
        instance = utils.translate.multiple_translations(instance=instance)
    except:
        pass
