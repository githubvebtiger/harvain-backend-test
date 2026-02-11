# region				-----External Imports-----
from django.apps import AppConfig

# endregion


class FinanceConfig(AppConfig):
    name = "finance"

    def ready(self):
        from finance import signals
