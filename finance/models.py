import uuid

from django import utils

# region				-----External Imports-----
from django.db import models

# region				-----Internal Imports-----
from . import choices

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class Transaction(models.Model):
    # region           -----Information-----
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    amount = models.FloatField(verbose_name="Сума", blank=False, null=False)

    comment = models.TextField(verbose_name="Коментар", blank=True, null=True)

    type = models.PositiveSmallIntegerField(
        choices=choices.types, verbose_name="Тип", blank=False, null=False, default=1
    )

    system = models.CharField(
        verbose_name="Платіжна система", max_length=100, blank=True, null=True
    )

    status = models.PositiveSmallIntegerField(
        choices=choices.statuses,
        verbose_name="Статус",
        blank=False,
        null=False,
        default=1,
    )

    last_migrate_datetime = models.DateTimeField(
        verbose_name="час останньої міграції",
        editable=False,
        default=utils.timezone.now,
    )

    created_at = models.DateTimeField(
        verbose_name="Дата та час", default=utils.timezone.now
    )
    # endregion

    # region           -----Relation-----
    client = models.ForeignKey(
        verbose_name="Клієнт",
        on_delete=models.CASCADE,
        related_name="transactions",
        blank=False,
        null=False,
        to="user.Client",
    )
    # endregion

    # region              -----Metas-----
    class Meta(object):
        verbose_name_plural = "Транзакції"
        verbose_name = "Транзакція"

    # endregion

    # region         -----Default Methods-----
    def __str__(self) -> str:
        return f"{self.id}"

    # endregion
