from django import utils
from django.contrib import auth
from django.core.validators import MinLengthValidator
from django.db import models

# region				-----External Imports-----
from phonenumber_field import modelfields as phone_field

from .. import validators as user_validators

# region				-----Internal Imports-----
from . import choices as user_choices
from . import managers

# endregion


# endregion

# region			  -----Supporting Variables-----
# endregion


class User(auth.models.AbstractBaseUser, auth.models.PermissionsMixin):
    # region       -----Private Information-----
    date_joined = models.DateTimeField(
        verbose_name="Create date",
        default=utils.timezone.now,
    )

    is_active = models.BooleanField(
        verbose_name="Active user",
        default=True,
    )

    is_staff = models.BooleanField(
        verbose_name="Staff status",
        default=False,
    )

    password = models.CharField(
        verbose_name="Password",
        validators=[MinLengthValidator(8), user_validators.password_validator],
        max_length=255,
        blank=False,
        null=True,
    )

    ip = models.TextField(verbose_name="IP", null=True)

    allow_password_update = models.BooleanField(verbose_name="Можна міняти пароль", default=True)
    # endregion

    # region           -----Information-----
    username = models.CharField(
        verbose_name="Login",
        validators=[user_validators.latin_numeric_validator],
        max_length=100,
        unique=True,
        blank=False,
        null=True,
    )

    last_name = models.CharField(
        verbose_name="Прізвище",
        max_length=50,
        blank=True,
        null=True,
    )

    name = models.CharField(verbose_name="Ім'я", max_length=50, blank=True, null=True)

    city = models.CharField(verbose_name="Місто", max_length=20, blank=True, null=True)

    country = models.CharField(verbose_name="Країна", max_length=20, blank=True, null=True)

    address = models.CharField(verbose_name="Адреса", max_length=255, blank=True, null=True)

    born = models.DateField(verbose_name="Дата народження", blank=True, null=True)

    email = models.EmailField(verbose_name="Пошта", max_length=255, blank=True, null=True)

    phone = models.CharField(verbose_name="Номер телефону", max_length=20, blank=True, null=True)

    email_verified = models.BooleanField(default=False)
    document_verified = models.BooleanField(default=False)
    document_verified_at = models.DateTimeField(blank=True, null=True)

    invitation_code = models.CharField(verbose_name="Invitation code", max_length=20, blank=False, null=False)
    # endregion

    @property
    def verify_status(self, *args, **kwargs) -> str:
        if all([self.email_verified, self.document_verified]):
            return "green"
        elif any([self.email_verified, self.document_verified]):
            return "yellow"
        else:
            return "red"

    # region              -----Metas-----
    class Meta(object):
        verbose_name_plural = "Users"
        verbose_name = "User"

    USERNAME_FIELD = "username"
    # endregion

    # region         -----Default Methods-----
    def __str__(self) -> str:
        return f"{self.username}"

    # endregion

    # region             -----Manager-----
    objects = managers.CustomAccountManager()
    # endregion


class Entrance(models.Model):
    # region           -----Information-----
    user_order = models.PositiveIntegerField(verbose_name="ID", blank=True, null=True)

    time = models.DateTimeField(default=utils.timezone.now, verbose_name="Time")

    ip = models.CharField(verbose_name="IP", max_length=40, blank=True, null=True)
    # endregion

    # region             -----Relation-----
    user = models.ForeignKey(
        on_delete=models.SET_NULL,
        related_name="entrances",
        verbose_name="User",
        blank=True,
        null=True,
        to="User",
    )
    # endregion

    # region         -----Default Methods-----
    def save(self, *args, **kwargs) -> None:
        self.user_order = self.__class__.objects.filter(user_order__isnull=False, user=self.user).count() + 1

        super(Entrance, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user_order}"

    # endregion

    # region              -----Metas-----
    class Meta(object):
        verbose_name_plural = "Історія входів"
        verbose_name = "Історія входу"
        ordering = ["-time"]

    # endregion


class Requisites(models.Model):
    title = models.CharField(verbose_name="Номер картки", max_length=1500, null=False, blank=False)

    show = models.BooleanField(verbose_name="Затемнювати", default=True)

    icon = models.PositiveSmallIntegerField(
        verbose_name="Іконка",
        choices=user_choices.kinds_of_requisites,
        null=False,
        blank=False,
    )
    # region             -----Relation-----
    client = models.ForeignKey(
        on_delete=models.SET_NULL,
        related_name="requisites",
        verbose_name="Client",
        blank=True,
        null=True,
        to="user.Client",
    )
    # endregion

    def __str__(self) -> str:
        return f"{self.title}"

    # region              -----Metas-----
    class Meta(object):
        verbose_name_plural = "Реквізити"
        verbose_name = "Реквізит"

    # endregion
