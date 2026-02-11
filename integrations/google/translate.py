import logging

import modeltranslation
from django.conf import settings as django_settings
from django.db import models as django_models

# region				-----External Imports-----
from website.settings.django import google_cloud_client

# endregion

logger = logging.Logger(__file__)


class ModelTranslator(object):
    # region		     -----Public Methods-----
    def translate(self, instance: django_models.Model) -> django_models.Model:
        # Check if Google Cloud Translation is available
        if google_cloud_client is None:
            logger.warning("Google Cloud Translation client not available - skipping translation")
            return instance

        project_id = django_settings.GOOGLE_CLOUD_TRANSLATE_PROJECT_ID
        location = django_settings.GOOGLE_CLOUD_TRANSLATE_LOCATION

        parent = f"projects/{project_id}/locations/{location}"

        field_values = {}

        for field in self.__translatable_fields:
            value = getattr(instance, field, None)
            if value:
                field_values[field] = value

        field_values = {key: str(value) for key, value in field_values.items() if value}

        if field_values:
            response = google_cloud_client.translate_text(
                target_language_code=self.__language,
                contents=field_values.values(),
                mime_type="text/html",
                parent=parent,
                timeout=120,
            )
            logger.info(f"ModelTranslator: {response}")

            iterate_over = zip(response.translations, field_values.keys())

            for value, field in iterate_over:
                field = f"{field}_{self.__language}"
                value = value.translated_text
                setattr(instance, field, value)

        return instance

    # endregion

    # region		     -----Private Method-----
    def __init__(self, model: django_models.Model, to_language: str) -> None:
        self.__translatable_fields = (
            modeltranslation.manager.get_translatable_fields_for_model(model.__class__)
        )

        self.__language = to_language
        self.__model = model

    # endregion


def translate(instance: django_models.Model, to_language: str) -> django_models.Model:
    try:
        translator = ModelTranslator(to_language=to_language, model=instance)
        logger.info(f"translate: {translator}")
        return translator.translate(instance=instance)
    except:
        pass
