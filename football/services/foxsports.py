# region				-----External Imports-----
import datetime
import typing
from xml.etree import ElementTree

import requests
import xmltodict
from django import conf, utils

# region				-----Internal Imports-----
from .exceptions import FoxSportsException

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class RssParamsType(typing.TypedDict):
    partnerKey: str
    size: int
    tags: str


class FoxSportsClient:
    def __init__(self) -> None:
        self._host = "api.foxsports.com"
        self._key = "MB0Wehpmuj2lUhuRhQaafhBjAJqaPU244mlTDK1i"
        self._version = "v2"

    @property
    def rss_url(self) -> str:
        return f"https://{self._host}/{self._version}/content/optimized-rss"

    @property
    def rss_params(self, size: int = 7) -> RssParamsType:
        return {"partnerKey": self._key, "size": size, "tags": "fs/cfb"}

    def rss(self) -> ElementTree:
        try:
            return ElementTree.fromstring(requests.get(self.rss_url, params=self.rss_params).content)
        except requests.exceptions.RequestException as ex:
            raise FoxSportsException

    def rss_list(self):
        try:
            xml_response = requests.get(self.rss_url, params=self.rss_params).content
            dict_data = xmltodict.parse(xml_response)
            news_list = dict_data["rss"]["channel"]["item"]
            for article in news_list:
                article["image"] = article["media:content"]["@url"]
                article["date"] = datetime.datetime.strptime(article["pubDate"], "%a, %d %b %Y %H:%M:%S %z")
            return news_list
        except requests.exceptions.RequestException as ex:
            raise FoxSportsException
