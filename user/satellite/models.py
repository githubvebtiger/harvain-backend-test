# region				-----External Imports-----
from http import client

from django import utils
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Sum

from .. import validators as user_validators

# region				-----Internal Imports-----
from ..user import models as user_models

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class Satellite(user_models.User):
    # region           -----Information-----
    uuid = models.CharField(max_length=50, blank=False, null=False)

    order = models.PositiveSmallIntegerField(verbose_name="Номер у списку", blank=True, null=True)

    deposit = models.IntegerField(verbose_name="Депозит", default=None, blank=True, null=True)

    block_balance = models.IntegerField(verbose_name="Заблок баланс", blank=False, null=False)

    active_balance = models.IntegerField(verbose_name="Актив баланс", blank=False, null=False)

    withdrawal = models.IntegerField(verbose_name="Виведення", blank=False, null=False)

    interval = models.DurationField(verbose_name="Інтервал блок-актив", blank=True, null=True)
    second_interval = models.DurationField(verbose_name="Інтервал актив-виведення", blank=True, null=True)

    allow_auth = models.BooleanField(verbose_name="Дозволити логін в ОК", default=True)

    system = models.BooleanField(default=False)

    is_original = models.BooleanField(default=False)

    blocked = models.BooleanField(verbose_name="Заблокувати", default=True)

    message_for_blocked = models.TextField(
        verbose_name="Повідомлення для заблокованого",
        default="Your account has been blocked. Please contact technical support",
        blank=False,
        null=False,
    )

    password_visible = models.CharField(
        verbose_name="Password visible",
        max_length=255,
        validators=[MinLengthValidator(8), user_validators.password_validator],
        blank=False,
        null=True,
    )

    migration_time = models.DateTimeField(verbose_name="Migration date (unblock)", blank=True, null=True)
    second_migration_time = models.DateTimeField(
        verbose_name="Migration date (withdrawal)", blank=True, null=True
    )

    deposit_time = models.DateTimeField(verbose_name="Deposit date", blank=True, null=True)

    created_at = models.DateTimeField(verbose_name="Create date", editable=False, default=utils.timezone.now)
    # endregion

    # region           -----Relation-----
    satellite_client = models.ForeignKey(
        verbose_name="Client",
        on_delete=models.CASCADE,
        related_name="satellites",
        blank=False,
        null=True,
        to="Client",
    )
    # endregion

    class Meta:
        verbose_name_plural = "Усі сателіти"
        verbose_name = "Сателіт"

    # region         -----Default Methods-----
    def __str__(self) -> str:
        return f"{self.uuid} {self.username}"

    def save(self, *args, **kwargs) -> None:
        # Track balance transitions and update timestamps
        if self.pk:
            try:
                old = Satellite.objects.get(pk=self.pk)
                # Track deposit: save total amount whenever balances change and deposit not yet set
                old_total = (old.block_balance or 0) + (old.active_balance or 0) + (old.withdrawal or 0)
                new_total = (self.block_balance or 0) + (self.active_balance or 0) + (self.withdrawal or 0)
                
                # Detect migration (not a deposit change)
                is_migration = (
                    (old.block_balance and old.block_balance > (self.block_balance or 0) and (self.active_balance or 0) > (old.active_balance or 0)) or
                    (old.active_balance and old.active_balance > (self.active_balance or 0) and (self.withdrawal or 0) > (old.withdrawal or 0))
                )
                
                if new_total == 0 and old_total > 0:
                    # All zeroed — reset everything
                    self.deposit = 0
                    self.deposit_time = None
                    self.migration_time = None
                    self.second_migration_time = None
                elif not is_migration:
                    if old_total == 0 and new_total > 0:
                        # First deposit
                        self.deposit_time = utils.timezone.now()
                        self.deposit = new_total
                    elif new_total > 0 and (not self.deposit or self.deposit == 0):
                        self.deposit = new_total
                    elif new_total > (self.deposit or 0) and not self.migration_time:
                        self.deposit = new_total
                # Block → Active: block decreased, active increased
                if old.block_balance and old.block_balance > self.block_balance and self.active_balance > old.active_balance:
                    self.migration_time = utils.timezone.now()
                # Active → Withdrawal: active decreased, withdrawal increased
                if old.active_balance and old.active_balance > self.active_balance and self.withdrawal > old.withdrawal:
                    self.second_migration_time = utils.timezone.now()
            except Satellite.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        client = self.satellite_client

        if client is not None:
            client.total_balance = round(
                client.satellites.all().aggregate(Sum('block_balance'))['block_balance__sum'], 0
            )

            client.save()

    # endregion


class SatellitePasswords(models.Model):
    satellite = models.ForeignKey(to="user.Satellite", on_delete=models.CASCADE, related_name="passwords")

    old_password = models.CharField(max_length=255, null=True, blank=False, verbose_name="Старий пароль")

    new_password = models.CharField(max_length=255, null=True, blank=False, verbose_name="Новий пароль")

    created_at = models.DateTimeField(verbose_name="Дата зміни паролю", default=utils.timezone.now)

    # region              -----Metas-----
    class Meta(object):
        verbose_name_plural = "Паролі сателіту"
        verbose_name = "Пароль сателіту"

    # endregion
