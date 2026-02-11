from django import contrib, forms, http
from django.db import models

from .models import Trade


class TradeAdminForm(forms.ModelForm):
    class Meta:
        model = Trade
        exclude = ('exchange',)


class BetClientInlineAdmin(contrib.admin.StackedInline):
    model = Trade
    fk_name = "client"
    form = TradeAdminForm

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super(BetClientInlineAdmin, self).get_formset(request, obj, **kwargs)

    def get_queryset(self, request: http.HttpRequest) -> models.QuerySet:
        queryset = super(BetClientInlineAdmin, self).get_queryset(request=request)
        return queryset.filter(client=self.parent_obj)
