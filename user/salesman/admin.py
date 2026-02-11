# region				-----External Imports-----
from django import contrib

from ..client import admin as client_admins

# region				-----Internal Imports-----
from . import models as salesman_models

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


@contrib.admin.register(salesman_models.Salesman)
class SalesmanAdmin(contrib.admin.ModelAdmin):
    list_display = ["id", "name", "clients_filter_link"]
    inlines = [client_admins.ClientInlineAdmin]
