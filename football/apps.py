# region				-----External Imports-----
from django.apps import AppConfig

# endregion


class FootballConfig(AppConfig):
    name = "football"

    def ready(self):
        import football.signals
        import football.tasks
