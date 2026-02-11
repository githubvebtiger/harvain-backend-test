from django.conf import settings

# region				-----External Imports-----
from modeltranslation import translator

# region				-----Internal Imports-----
from . import models as football_models

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


@translator.register(football_models.League)
class LeagueTranslationOptions(translator.TranslationOptions):
    required_languages = [*settings.LANGUAGE_CODES]
    fields = ["title", "round"]


@translator.register(football_models.Match)
class MatchTranslationOptions(translator.TranslationOptions):
    required_languages = [*settings.LANGUAGE_CODES]
    fields = ["referee"]


@translator.register(football_models.Team)
class TeamTranslationOptions(translator.TranslationOptions):
    required_languages = [*settings.LANGUAGE_CODES]
    fields = ["title"]
