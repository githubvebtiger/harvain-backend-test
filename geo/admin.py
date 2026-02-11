# region				-----External Imports-----
from django.contrib import admin

# region				-----Internal Imports-----
from .models import Country

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]
