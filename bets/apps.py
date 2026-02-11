# region				-----External Imports-----
from django.apps import AppConfig

# endregion


class BetsConfig(AppConfig):
    name = "bets"

    def ready(self) -> None:
        import bets.signals
