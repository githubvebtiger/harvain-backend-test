# region				-----External Imports-----
import dataclasses
import datetime
import os
import typing

import requests

import utils

# region				-----Internal Imports-----
from . import exceptions

# endregion

# endregion


@dataclasses.dataclass
class RapidAPI(object):
    version: str or None
    path: str
    host: str

    # region		     -----Private Method-----
    def __post_init__(self):
        self.secret_key = os.environ.get("RAPID_API_KEY")
        self.url = self.__build_url()
        self.headers = self.__request_headers()

    def __build_url(self) -> typing.AnyStr:
        if self.version:
            return "https://{host}/{version}/{path}/".format(
                version=self.version, path=self.path, host=self.host
            )
        else:
            return "https://{host}/{path}/".format(path=self.path, host=self.host)

    def __request_headers(self) -> typing.Dict:
        return {"X-RapidAPI-Key": self.secret_key, "X-RapidAPI-Host": self.host}

    # endregion

    # region		     -----Public Methods-----
    def fetch_data(self, search_by: typing.Dict) -> typing.List[typing.Dict]:
        try:
            response = requests.get(
                headers=self.headers, params=search_by, url=self.url
            ).json()
            return response.get("response")
        except requests.exceptions.RequestException:
            raise exceptions.RapidException

    # endregion
