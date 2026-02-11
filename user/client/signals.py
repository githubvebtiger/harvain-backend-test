import typing
import uuid

from django import dispatch, forms, utils
from django.core.exceptions import ObjectDoesNotExist

# region				-----External Imports-----
from django.db.models import Sum, signals

from history.middleware import get_current_user
from history.models import HistoryLog
from .models import Client

from ..satellite import models as satellite_models

# region				-----Internal Imports-----
from . import models as client_models

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


@dispatch.receiver(signals.pre_save, sender=client_models.Client)
def client_creating(instance: client_models.Client, raw: bool = True, **kwargs: typing.Dict) -> None:
    if raw:  # if data saves from loaddata
        return

    try:
        client = Client.objects.get(pk=instance.pk)
        # Only reset email_verified if email was actually changed by user
        # (both old and new must be non-empty and different)
        old_email = (client.email or '').strip().lower()
        new_email = (instance.email or '').strip().lower()
        if old_email and new_email and old_email != new_email:
            instance.email_verified = False
            # Also reset email_verified for all satellites of this client
            satellite_models.Satellite.objects.filter(
                satellite_client_id=instance.pk
            ).update(email_verified=False)
    except Client.DoesNotExist:
        pass

    if instance.pk:
        original_user = client_models.Client.objects.get(pk=instance.pk)
        if instance.password_visible != original_user.password_visible:
            client_models.ClientPasswords.objects.create(
                client=instance,
                old_password=original_user.password_visible,
                new_password=instance.password_visible,
            )
            instance.set_password(instance.password_visible)

    else:
        instance.set_password(instance.password_visible)
    instance.adding = instance._state.adding


@dispatch.receiver(signals.post_save, sender=client_models.Client)
def client_after_creating(instance: client_models.Client, raw: bool = True, **kwargs: typing.Dict) -> None:
    if raw:  # if data saves from loaddata
        return
    
    if instance.adding:
        system_satellites = (
            satellite_models.Satellite.objects.filter(system=True).filter(satellite_client__isnull=True).all()
        )
        for satellite in system_satellites:
            if satellite.deposit and instance.shoulder is not None and instance.growth_rate is not None:
                block_b = satellite.deposit * instance.shoulder * (instance.growth_rate * 0.01 + 1) * (
                    1 - instance.commission
                ) - (satellite.deposit * instance.shoulder)
            else:
                block_b = 0

            satellite_data = {
                **forms.model_to_dict(
                    satellite,
                    exclude=[
                        "id",
                        "satellite_client",
                        "user_ptr",
                        "groups",
                        "user_permissions",
                        "is_original",
                    ],
                ),
                "username": f"{satellite.username}_{uuid.uuid4()}",
                "phone": instance.phone,
                "email": instance.email,
                "country": instance.country,
                "name": instance.username,
                "last_name": instance.full_name,
                "satellite_client": instance,
                "block_balance": round(block_b, 1),
            }
            satellite_models.Satellite.objects.create(**satellite_data)


@dispatch.receiver(signals.pre_delete, sender=client_models.Client)
def client_before_removal(instance: client_models.Client, **kwargs: typing.Dict) -> None:
    current_user = get_current_user()

    user_fields = ["username", "password_visible", "full_name", "salesman"]

    result = {
        "satellites": [],
        "bets": [],
        "transactions": [],
        "entrances": [],
        "passwords": [],
        "requisites": [],
        "client": {field_name: getattr(instance, field_name) for field_name in user_fields},
    }

    for satellite in instance.satellites.all():
        mini_result = {}
        for field in satellite._meta.fields:
            if satellite.system:
                field_name = field.name
                field_value = getattr(satellite, field_name)
                mini_result[field_name] = field_value

        result["satellites"].append(mini_result)

    for bet in instance.bets.all():
        mini_result = {}
        for field in bet._meta.fields:

            field_name = field.name
            field_value = getattr(bet, field_name)
            mini_result[field_name] = field_value

        result["bets"].append(mini_result)

    for transaction in instance.transactions.all():
        mini_result = {}
        for field in transaction._meta.fields:

            field_name = field.name
            field_value = getattr(transaction, field_name)
            mini_result[field_name] = field_value

        result["transactions"].append(mini_result)

    for entrance in instance.entrances.all():
        mini_result = {}
        for field in entrance._meta.fields:

            field_name = field.name
            field_value = getattr(entrance, field_name)
            mini_result[field_name] = field_value

        result["entrances"].append(mini_result)

    for password in instance.passwords.all():
        mini_result = {}
        for field in password._meta.fields:

            field_name = field.name
            field_value = getattr(password, field_name)
            mini_result[field_name] = field_value

        result["passwords"].append(mini_result)

    for requisite in instance.requisites.all():
        mini_result = {}
        for field in requisite._meta.fields:

            field_name = field.name
            field_value = getattr(requisite, field_name)
            mini_result[field_name] = field_value

        result["requisites"].append(mini_result)

    if current_user and str(current_user) != "AnonymousUser":
        HistoryLog.objects.create(
            type="client removal",
            change_message=f"client {instance.pk}:\n {instance.full_name} was deleted",
            user=current_user,
            client=instance.full_name,
            salesman=instance.salesman,
            additional_info=str(result),
        )
