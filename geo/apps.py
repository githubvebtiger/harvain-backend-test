# region				-----External Imports-----
from django.apps import AppConfig

# endregion


class GeoConfig(AppConfig):
    name = "geo"

    def ready(self) -> None:
        import geo.signals
