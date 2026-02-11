# region				-----External Imports-----
from django import utils
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.html import mark_safe

from .. import validators as user_validators

# region				-----Internal Imports-----
from ..user import models as user_models

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class Client(user_models.User):
    # region           -----Information-----
    full_name = models.CharField(verbose_name="ПІ (для себе)", max_length=300, blank=False, null=False)

    password_visible = models.CharField(
        verbose_name="Пароль від чистилища",
        validators=[MinLengthValidator(8), user_validators.password_validator],
        max_length=255,
        blank=False,
        null=True,
    )

    created_at = models.DateTimeField(verbose_name="Create date", editable=False, default=utils.timezone.now)
    total_balance = models.BigIntegerField(verbose_name="Total balance", default=0)
    # endregion

    # region           -----Relation-----
    salesman = models.ForeignKey(
        verbose_name="Продавець",
        on_delete=models.CASCADE,
        related_name="clients",
        blank=True,
        null=True,
        to="Salesman",
    )

    shoulder = models.FloatField(verbose_name="Плече", default=None, null=True, blank=True)
    growth_rate = models.FloatField(verbose_name="Відсоток росту", default=None, null=True, blank=True)
    commission = models.FloatField(verbose_name="Комісія біржі", default=0.00025)
    # endregion

    class Meta:
        verbose_name_plural = "Клієнти"
        verbose_name = "Клієнт"

    # region         -----Default Methods-----
    def __str__(self) -> str:
        return f"{self.full_name}"

    # endregion

    def save(self, *args, **kwargs) -> None:

        if self.pk:
            user_before = Client.objects.get(pk=self.pk)
        else:
            user_before = None

        super().save(*args, **kwargs)
        
        # Sync email_verified status to all satellites when changed in admin
        if user_before and user_before.email_verified != self.email_verified:
            self.satellites.update(email_verified=self.email_verified)
            
        # Sync document_verified status to all satellites when changed in admin
        if user_before and user_before.document_verified != self.document_verified:
            self.satellites.update(
                document_verified=self.document_verified,
                document_verified_at=self.document_verified_at
            )

        if user_before and (
            user_before.shoulder != self.shoulder
            or user_before.growth_rate != self.growth_rate
            or user_before.commission != self.commission
        ):
            for sat in self.satellites.filter(system=True):
                if sat.deposit and self.shoulder is not None and self.growth_rate is not None:
                    result = (
                        sat.deposit * self.shoulder * (self.growth_rate * 0.01 + 1) * (1 - self.commission)
                        - (sat.deposit * self.shoulder),
                    )
                    if sat.active_balance:
                        sat.active_balance = result
                    elif sat.withdrawal:
                        sat.withdrawal = result
                    else:
                        if isinstance(result, tuple):
                            sat.block_balance = int(result[0])
                        else:
                            sat.block_balance = result
                else:
                    sat.block_balance = 0
                sat.save()

    # region         -----Additional Methods-----
    def satellites_filter_link(self) -> str:
        return mark_safe(
            f"""
            <a href='/admin/user/satellite/?satellite_client__user_ptr__exact={self.pk}'>
                Сателіти
            </a>"""
        )

    satellites_filter_link.short_description = "сателіти"
    satellites_filter_link.allow_tags = True
    # endregion


class ClientPasswords(models.Model):
    client = models.ForeignKey(to="user.Client", on_delete=models.CASCADE, related_name="passwords")

    old_password = models.CharField(max_length=255, null=True, blank=False, verbose_name="Старий пароль")

    new_password = models.CharField(max_length=255, null=True, blank=False, verbose_name="Новий пароль")

    created_at = models.DateTimeField(verbose_name="Дата зміни паролю", default=utils.timezone.now)

    # region              -----Metas-----
    class Meta(object):
        verbose_name_plural = "Паролі клієнта"
        verbose_name = "Пароль клієнта"

    # endregion


class SupportTicket(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    account_number = models.CharField(max_length=6)
    subject = models.CharField(max_length=255)
    description = models.TextField()


class PricingPlan(models.Model):
    full_name = models.CharField(max_length=255)
    total_price = models.CharField(max_length=255)
    requisite = models.CharField(max_length=255)
    to_be_paid = models.CharField(max_length=255)


class Payment(models.Model):
    full_name = models.CharField(max_length=255)
    total_price = models.CharField(max_length=255)
    requisite = models.CharField(max_length=255)
    to_be_paid = models.CharField(max_length=255)
    user = models.ForeignKey(Client, on_delete=models.CASCADE)
