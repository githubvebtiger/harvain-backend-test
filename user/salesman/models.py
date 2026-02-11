from django.db import models
from django.utils.html import mark_safe


class Salesman(models.Model):
    name = models.CharField(
        verbose_name="Name", max_length=255, blank=False, null=False
    )

    class Meta(object):
        verbose_name_plural = "Продавці"
        verbose_name = "Продавець"

    def __str__(self) -> str:
        return f"{self.name}"

    def clients_filter_link(self) -> str:
        return mark_safe(
            f"""
            <a href='/admin/user/client/?salesman__id__exact={self.pk}'>
                Clients
            </a>"""
        )

    clients_filter_link.short_description = "Clients"
    clients_filter_link.allow_tags = True
