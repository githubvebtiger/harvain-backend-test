from django.conf import settings

# region				-----External Imports-----
from modeltranslation import translator

# region				-----Internal Imports-----
from . import models as bet_models

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


@translator.register(bet_models.OddsDetail)
class OddDetailTranslationOptions(translator.TranslationOptions):
    required_languages = [*settings.LANGUAGE_CODES]
    fields = ["name"]


@translator.register(bet_models.Odds)
class OddTranslationOptions(translator.TranslationOptions):
    required_languages = [*settings.LANGUAGE_CODES]
    fields = ["name"]
