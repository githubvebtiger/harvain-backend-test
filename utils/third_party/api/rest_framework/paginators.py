import typing

# region				-----External Imports-----
from rest_framework import pagination as rest_pagination
from rest_framework import response as rest_response

# endregion


class StandartPagePaginator(rest_pagination.PageNumberPagination):
    page_size_query_param: str = "page_size"
    max_page_size: int = 10_000
    page_size: int = 10_000

    def get_paginated_response(self, data: typing.Iterable) -> rest_response.Response:
        return rest_response.Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "results": data,
            }
        )
