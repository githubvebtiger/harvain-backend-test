import typing

from django import dispatch
from django.core.exceptions import ObjectDoesNotExist

# region				-----External Imports-----
from django.db.models import Sum, signals

from history.middleware import get_current_user
from history.models import HistoryLog

# region				-----Internal Imports-----
from .. import models as satellite_models

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


@dispatch.receiver(signals.pre_save, sender=satellite_models.Satellite)
def satellite_creating(instance: satellite_models.Satellite, raw: bool = True, **kwargs: typing.Dict) -> None:
    if raw:  # if data saves from loaddata
        return

    if instance.pk:
        # Password hashing - always check and hash password regardless of current_user
        try:
            satellite_before = satellite_models.Satellite.objects.get(pk=instance.pk)
            if instance.password_visible and instance.password_visible != satellite_before.password_visible:
                instance.set_password(instance.password_visible)
                # Create password history record (without requiring current_user)
                try:
                    satellite_models.SatellitePasswords.objects.create(
                        satellite=instance,
                        old_password=satellite_before.password_visible,
                        new_password=instance.password_visible,
                    )
                except Exception:
                    pass  # Don't fail if history creation fails
        except ObjectDoesNotExist:
            pass

        try:
            current_user = get_current_user()
            if not current_user or str(current_user) == "AnonymousUser":
                raise ObjectDoesNotExist

            satellite_before = satellite_models.Satellite.objects.get(pk=instance.pk)
            changes = []
            
            # Sync profile data from Satellite to Client
            if instance.satellite_client:
                client = instance.satellite_client
                profile_fields_changed = False
                
                # Check and sync profile fields
                if instance.name != satellite_before.name:
                    client.name = instance.name
                    profile_fields_changed = True
                
                if instance.last_name != satellite_before.last_name:
                    client.last_name = instance.last_name
                    profile_fields_changed = True
                
                if instance.country != satellite_before.country:
                    client.country = instance.country
                    profile_fields_changed = True
                
                if instance.city != satellite_before.city:
                    client.city = instance.city
                    profile_fields_changed = True
                
                if instance.address != satellite_before.address:
                    client.address = instance.address
                    profile_fields_changed = True
                
                if instance.born != satellite_before.born:
                    client.born = instance.born
                    profile_fields_changed = True
                
                if instance.phone != satellite_before.phone:
                    client.phone = instance.phone
                    profile_fields_changed = True
                
                # Only reset email_verified if email was actually changed
                # (both old and new must be non-empty and different)
                old_email = (satellite_before.email or '').strip().lower()
                new_email = (instance.email or '').strip().lower()
                if old_email and new_email and old_email != new_email:
                    client.email = instance.email
                    # Reset email verification when email changes
                    client.email_verified = False
                    instance.email_verified = False
                    profile_fields_changed = True

                    # Also reset email_verified for all satellites of this client
                    satellite_models.Satellite.objects.filter(
                        satellite_client_id=client.id
                    ).exclude(pk=instance.pk).update(email_verified=False)
                elif instance.email != satellite_before.email:
                    # Email changed but not a "real" change (e.g., empty -> value or case change)
                    client.email = instance.email
                    profile_fields_changed = True
                
                # Save client if any profile fields changed
                if profile_fields_changed:
                    client.save()
            
            if instance.system:
                client = instance.satellite_client
                if (
                    instance.deposit != satellite_before.deposit
                    and client is not None
                    and client.shoulder is not None
                    and client.growth_rate is not None
                ):
                    result = instance.deposit * client.shoulder * (client.growth_rate * 0.01 + 1) * (
                        1 - client.commission
                    ) - (instance.deposit * client.shoulder)

                    if instance.active_balance:
                        instance.active_balance = result
                    elif instance.withdrawal:
                        instance.withdrawal = result
                    else:
                        instance.block_balance = result

                    client.total_balance = round(
                        client.satellites.all().aggregate(Sum('block_balance'))['block_balance__sum'], 0
                    )
                    client.save()

                if instance.uuid != satellite_before.uuid:
                    if instance.satellite_client:
                        HistoryLog.objects.create(
                            type="satellite id change",
                            change_message=f"satellite {instance.pk}:\nuuid change {satellite_before.uuid} -> {instance.uuid}",
                            user=current_user,
                            client=instance.satellite_client,
                            salesman=instance.satellite_client.salesman,
                        )
                    else:
                        HistoryLog.objects.create(
                            type="satellite id change",
                            change_message=f"satellite {instance.pk}:\nuuid change {satellite_before.uuid} -> {instance.uuid}",
                            user=current_user,
                            client="None",
                            salesman=None,
                        )

                if instance.password_visible != satellite_before.password_visible:
                    changes.append(
                        f"password change {satellite_before.password_visible} -> {instance.password_visible}"
                    )

                if instance.username != satellite_before.username:
                    changes.append(f"username change {satellite_before.username} -> {instance.username}")

                if changes:
                    if instance.satellite_client:
                        HistoryLog.objects.create(
                            type="satellite login change",
                            change_message=f"satellite {instance.pk}:\n" + ",\n".join(changes),
                            user=current_user,
                            client=instance.satellite_client,
                            salesman=instance.satellite_client.salesman,
                        )
                    else:
                        HistoryLog.objects.create(
                            type="satellite login change",
                            change_message=f"satellite {instance.pk}:\n" + ",\n".join(changes),
                            user=current_user,
                            client="None",
                            salesman=None,
                        )

                    changes = []

                if instance.block_balance != satellite_before.block_balance:
                    changes.append(f"block_balance change {satellite_before.block_balance} -> {instance.block_balance}")

                if instance.active_balance != satellite_before.active_balance:
                    changes.append(
                        f"active_balance change {satellite_before.active_balance} -> {instance.active_balance}"
                    )

                if instance.withdrawal != satellite_before.withdrawal:
                    changes.append(f"withdrawal change {satellite_before.withdrawal} -> {instance.withdrawal}")

                if changes:
                    if instance.satellite_client:
                        HistoryLog.objects.create(
                            type="satellite balance change",
                            change_message=f"satellite {instance.pk}:\n" + ",\n".join(changes),
                            user=current_user,
                            client=instance.satellite_client,
                            salesman=instance.satellite_client.salesman,
                        )
                    else:
                        HistoryLog.objects.create(
                            type="satellite balance change",
                            change_message=f"satellite {instance.pk}:\n" + ",\n".join(changes),
                            user=current_user,
                            client="None",
                            salesman=None,
                        )

        except ObjectDoesNotExist:
            pass
    else:
        instance.set_password(instance.password_visible)
