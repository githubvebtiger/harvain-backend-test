from typing import Any

from django.contrib.admin import ModelAdmin, StackedInline, display, register
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import models
from django.http import HttpRequest

from . import forms as user_forms
from . import models as user_models


@register(user_models.User)
class UserAdmin(BaseUserAdmin):
    form = user_forms.UserAdminChangingForm
    add_form = user_forms.UserAdminCreationForm
    list_display = ["id", "username", "email", "name", "is_staff"]
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "username",
                    "email",
                    "name",
                    "last_name",
                    "is_staff",
                    "password",
                ]
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ["username", "name", "last_name", "password", "password_2"],
            },
        ),
    )
    search_fields = (
        "username",
        "email",
    )
    ordering = ("id", "username", "email")

    def get_queryset(self, request: HttpRequest) -> models.QuerySet:
        queryset = (
            super(UserAdmin, self)
            .get_queryset(request=request)
            .prefetch_related("entrances")
            .filter(satellite__isnull=True, client__isnull=True)
        )
        return queryset


@register(user_models.Requisites)
class RequisitesAdmin(ModelAdmin):
    list_display = ["id", "title", "show", "icon"]
    fields = ["title", "show", "icon"]


class UserEntrancesInline(StackedInline):
    readonly_fields = ["ip", "_time"]
    fields = ["ip", "_time"]

    @display(description="Время")
    def _time(self, instance):
        return instance.time.strftime("%d/%m/%Y, %H:%M")

    model = user_models.Entrance
    can_delete = False
    max_num = 0
    extra = 0


class RequisitesInline(StackedInline):
    fields = ["title", "show", "icon"]
    model = user_models.Requisites
