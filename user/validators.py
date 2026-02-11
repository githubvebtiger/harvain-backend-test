from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class MaximumLengthValidator:
    def __init__(self, max_length=30):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                _(
                    "Password length exceeds the maximum limit of %(max_length)d characters."
                ),
                code="password_max_length",
                params={"max_length": self.max_length},
            )

    def get_help_text(self):
        return _(
            "Your password must not exceed %(max_length)d characters in length."
        ) % {"max_length": self.max_length}


class UppercaseValidator:
    def validate(self, password, user=None):
        if not any(char.isupper() for char in password):
            raise ValidationError(
                _("The password must contain at least one uppercase letter."),
                code="password_no_uppercase",
            )

    def get_help_text(self):
        return _("Your password must contain at least one uppercase letter.")


class LatinCharacterValidator:
    def validate(self, password, user=None):
        if not password.isascii():
            raise ValidationError(
                _("The password must contain only Latin characters."),
                code="password_non_latin",
            )

    def get_help_text(self):
        return _("Your password must contain only Latin characters.")


latin_numeric_validator = RegexValidator(
    regex=r"^[a-zA-Z0-9\-\_\s]+$",
    message="This field must contain only Latin characters and numbers.",
)

password_validator = RegexValidator(
    regex=r"(?=.*[A-Z])(?=.*\d)[A-Za-z\d_-]{8,30}$",
    message="Password must be between 8 and 30 characters, contain at least one uppercase letter, one digit, and only Latin characters.",
)
