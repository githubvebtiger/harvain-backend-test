# region			  -----Supporting Variables-----
gettext = lambda s: s
# endregion

LANGUAGES = (
    ("en-us", gettext("us")),
    ("es", gettext("es")),
    ("fr", gettext("fr")),
)

LANGUAGE_CODE = "en-us"

LANGUAGE_CODES = [language[0] for language in LANGUAGES]
