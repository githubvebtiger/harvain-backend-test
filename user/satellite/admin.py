from django import contrib, http
from django.db import models

from ..user import admin as user_admin
from . import forms as satellite_forms
from . import models as satellite_models


class SatellitePasswordsInlineAdmin(contrib.admin.StackedInline):
    model = satellite_models.SatellitePasswords
    fields = ["old_password", "new_password", "created_at"]
    readonly_fields = ["old_password", "new_password", "created_at"]

    can_delete = False
    max_num = 0
    extra = 0

    def get_queryset(self, request: http.HttpRequest):
        queryset = super().get_queryset(request=request)
        last = queryset.last()
        if last:
            last_three = queryset.all().order_by("-id").filter(id__gt=last.id - 3)
        else:
            last_three = queryset
        return last_three


@contrib.admin.register(satellite_models.Satellite)
class SatelliteAdmin(contrib.admin.ModelAdmin):
    form = satellite_forms.SatelliteAdminForm
    list_display = [
        "uuid",
        "deposit",
        "block_balance",
        "active_balance",
        "withdrawal",
        "interval",
        "second_interval",
        "blocked",
        "migration_time",
        "second_migration_time",
        "is_original",
    ]
    list_filter = ["system", "satellite_client"]
    inlines = [user_admin.UserEntrancesInline, SatellitePasswordsInlineAdmin]
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "uuid",
                    "username",
                    "password_visible",
                    "deposit",
                    "block_balance",
                    "active_balance",
                    "withdrawal",
                    "interval",
                    "second_interval",
                    "allow_auth",
                    "blocked",
                    "allow_password_update",
                    "phone",
                    "email",
                    "born",
                    "address",
                    "country",
                    "city",
                    "name",
                    "last_name",
                    "is_original",
                ]
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": [
                    "uuid",
                    "username",
                    "block_balance",
                    "active_balance",
                    "withdrawal",
                    "interval",
                    "second_interval",
                    "password_visible",
                    "allow_auth",
                    "blocked",
                    "allow_password_update",
                    "phone",
                    "email",
                    "born",
                    "address",
                    "country",
                    "city",
                    "name",
                    "last_name",
                    "is_original",
                ]
            },
        ),
    )

    def get_queryset(sefl, request):
        queryset = super().get_queryset(request=request)
        return queryset.prefetch_related("entrances")


class SatelliteClientInlineAdmin(contrib.admin.StackedInline):
    form = satellite_forms.SatelliteInlineForm
    model = satellite_forms.Satellite
    verbose_name_plural = "Сателіти"
    fk_name = "satellite_client"
    fields = [
        "uuid",
        "username",
        "password_visible",
        "block_balance",
        "active_balance",
        "withdrawal",
        "order",
        "message_for_blocked",
        "allow_auth",
        "blocked",
        "allow_password_update",
        "is_original",
    ]

    def save_model(self, request: http.HttpRequest, obj: satellite_models.Satellite, change, form):
        obj.system = False
        obj.save()

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super(SatelliteClientInlineAdmin, self).get_formset(request, obj, **kwargs)

    def get_queryset(self, request: http.HttpRequest) -> models.QuerySet:
        queryset = super(SatelliteClientInlineAdmin, self).get_queryset(request=request)
        return queryset.filter(satellite_client=self.parent_obj, system=False)
