import logging
import traceback
import typing

from django import http as django_http

# region				-----External Imports-----
from django.utils.translation import gettext_lazy as _

from website import settings as website_settings

# endregion

# region			  -----Supporting Variables-----
logger = logging.getLogger(__file__)
# endregion

# endregion


class Process500Error(object):
    def __init__(self, get_response: typing.Callable) -> None:
        self._get_response = get_response

    def __call__(self, request: typing.Dict) -> typing.Dict:
        return self._get_response(request)

    def process_exception(self, request: django_http.HttpRequest, exception: Exception) -> django_http.JsonResponse:
        logger.error(traceback.format_exc())

        response_data = {"detail": _("Something went wrong"), "success": False}

        if website_settings.DEBUG:
            trace_back = {"traceback": traceback.format_exc().split("\n")}

            response_data.update(trace_back)

        return django_http.JsonResponse(response_data, status=500)
