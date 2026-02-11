import typing

from django import dispatch
from django.core.exceptions import ObjectDoesNotExist
from django.db import models as django_models

from history.middleware import get_current_user
from history.models import HistoryLog

from . import models


@dispatch.receiver(signal=django_models.signals.pre_save, sender=models.Transaction)
def change_transaction(instance: typing.Any, raw: bool = True, *args, **kwargs) -> None:
    if raw:  # if data saves from loaddata
        return
    
    if instance.pk:
        try:

            current_user = get_current_user()
            if not current_user or str(current_user) == "AnonymousUser":
                raise ObjectDoesNotExist

            transaction_before = models.Transaction.objects.get(pk=instance.pk)
            changes = []

            if instance.id != transaction_before.id:
                changes.append(f"id changed {transaction_before.id} -> {instance.id}")

            if instance.amount != transaction_before.amount:
                changes.append(f"amount changed {transaction_before.amount} -> {instance.amount}")

            if instance.comment != transaction_before.comment:
                changes.append(f"comment changed {transaction_before.comment} -> {instance.comment}")

            if instance.type != transaction_before.type:
                changes.append(f"type changed {transaction_before.type} -> {instance.type}")

            if instance.system != transaction_before.system:
                changes.append(f"system changed {transaction_before.system} -> {instance.system}")

            if instance.status != transaction_before.status:
                changes.append(f"status changed {transaction_before.status} -> {instance.status}")
            if instance.last_migrate_datetime != transaction_before.last_migrate_datetime:
                changes.append(
                    f"last_migrate_datetime changed {transaction_before.last_migrate_datetime} -> {instance.last_migrate_datetime}"
                )
            if instance.created_at != transaction_before.created_at:
                changes.append(f"created_at changed {transaction_before.created_at} -> {instance.created_at}")
            if instance.client != transaction_before.client:
                changes.append(f"client changed {transaction_before.client} -> {instance.client}")

            if changes:
                HistoryLog.objects.create(
                    type="transaction change",
                    change_message=f"transaction {instance.pk}:\n" + ",\n".join(changes),
                    user=current_user,
                    client=instance.client.full_name,
                    salesman=instance.client.salesman,
                )
        except ObjectDoesNotExist:
            pass


@dispatch.receiver(signal=django_models.signals.pre_delete, sender=models.Transaction)
def delete_transaction(instance: typing.Any, *args, **kwargs) -> None:
    current_user = get_current_user()
    if current_user and str(current_user) != "AnonymousUser":
        HistoryLog.objects.create(
            type="transaction removal",
            change_message=f"transaction {instance.pk}: was deleted",
            user=current_user,
            client=instance.client.full_name,
            salesman=instance.client.salesman,
        )
