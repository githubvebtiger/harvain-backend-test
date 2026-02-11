# region				-----External Imports-----
import dataclasses

# region				-----Internal Imports-----
from . import api

# endregion

# endregion


@dataclasses.dataclass
class FixtureHandler(object):
    api: api.RapidAPI


@dataclasses.dataclass
class OddsHandler(object):
    api: api.RapidAPI
