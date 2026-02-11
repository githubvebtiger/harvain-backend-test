import copy

# region				-----External Imports-----
import logging
import typing

from django import dispatch
from django.conf import settings
from django.db import models as django_models

import utils
from football import models as football_models
from geo import models as geo_models
from integrations import google

from ... import models

# endregion

# region				-----Internal Imports-----
logger = logging.Logger(__file__)
# endregion


@dispatch.receiver(signal=django_models.signals.pre_save, sender=models.Country)
def translate_country(instance: typing.Any, raw: bool = True, *args, **kwargs) -> None:
    if raw:  # if data saves from loaddata
        return
    
    try:
        instance = utils.translate.multiple_translations(instance=instance)
    except:
        pass
