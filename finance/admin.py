import typing

# region				-----External Imports-----
from django import contrib, http
from django.db import models

from user import models as user_models

# region				-----Internal Imports-----
from .models import Transaction

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


# @contrib.admin.register(Transaction)
# class TransactionAdmin(contrib.admin.ModelAdmin):
#     list_display = ["id", "amount", "type", "client_", "created_at"]

#     def get_queryset(self, request: http.HttpRequest)\
#         -> models.QuerySet:
#         queryset = super(TransactionAdmin, self)\
#             .get_queryset(request=request)

#         return queryset\
#             .annotate(_client=\
#                 user_models.Client.objects\
#                     .filter(id=models.OuterRef("client"))\
#                     .values("full_name")
#             )

#     @contrib.admin.display(description="Client",
#                    ordering='_client')
#     def client_(self, instance: Transaction)\
#         -> typing.AnyStr:
#         return instance._client


class TransactionClientInlineAdmin(contrib.admin.StackedInline):
    model = Transaction
    fk_name = "client"

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super(TransactionClientInlineAdmin, self).get_formset(
            request, obj, **kwargs
        )

    def get_queryset(self, request: http.HttpRequest) -> models.QuerySet:
        queryset = super(TransactionClientInlineAdmin, self).get_queryset(
            request=request
        )
        return queryset.filter(client=self.parent_obj)
