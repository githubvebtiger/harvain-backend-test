from django.contrib.auth import models

# region				-----External Imports-----
from django.utils.translation import gettext_lazy as _

# endregion


class CustomAccountManager(models.BaseUserManager):
    def create_superuser(self, username, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True.")
        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True.")
        return self.create_user(username, password, **other_fields)

    def create_user(self, username, password, **other_fields):
        if not username:
            raise ValueError(_("You must provide an username address"))

        if "email" in other_fields and other_fields["email"]:
            other_fields["email"] = self.normalize_email(other_fields["email"])

        user = self.model(username=username, **other_fields)
        user.set_password(password)
        user.save()
        return user
