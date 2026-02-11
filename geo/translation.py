from django.conf import settings

# region				-----External Imports-----
from modeltranslation import translator

# region				-----Internal Imports-----
from . import models as geo_models

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


@translator.register(geo_models.Country)
class CountryTranslationOptions(translator.TranslationOptions):
    required_languages = [*settings.LANGUAGE_CODES]
    fields = ["title"]
