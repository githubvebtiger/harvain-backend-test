import logging
import typing

# region				-----External Imports-----
from django.conf import settings

from integrations import google

# region				-----Internal Imports-----
logger = logging.Logger(__file__)
# endregion


def multiple_translations(instance: typing.Any) -> None:
    if instance._state.adding:
        LANGUAGE_CODES = [code for code in settings.LANGUAGE_CODES if code != "en-us"]
        for language in LANGUAGE_CODES:
            instance = google.translate.translate(
                to_language=language, instance=instance
            )

    return instance
