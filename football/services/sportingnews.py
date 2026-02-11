# region				-----External Imports-----
import datetime
import typing
from xml.etree import ElementTree

import requests
import xmltodict

# region				-----Internal Imports-----
from .exceptions import SportingNewsException

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class SportingNewsClient:
    def __init__(self) -> None:
        self._host = "www.sportingnews.com"

    @property
    def rss_url(self) -> str:
        return f"https://{self._host}/us/rss"

    def rss(self) -> typing.List[typing.Any]:
        try:
            return ElementTree.fromstring(requests.get(self.rss_url).content)
        except requests.exceptions.RequestException as ex:
            raise SportingNewsException

    def rss_list(self):
        try:
            xml_response = requests.get(self.rss_url).content
            dict_data = xmltodict.parse(xml_response)
            news_list = dict_data["rss"]["channel"]["item"]
            for article in news_list:
                if isinstance(article["media:content"], list):
                    article["image"] = article["media:content"][0]["@url"]
                else:
                    article["image"] = article["media:content"]["@url"]
                article["date"] = datetime.datetime.strptime(article["pubDate"], "%a, %d %b %Y %H:%M:%S %z")
            return news_list
        except requests.exceptions.RequestException as ex:
            raise SportingNewsException
