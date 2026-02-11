# region				-----External Imports-----
from django import forms

# region				-----Internal Imports-----
from .models import Satellite

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class SatelliteLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class SatelliteInlineForm(forms.ModelForm):
    class Meta:
        model = Satellite
        fields = [
            "uuid",
            "username",
            "block_balance",
            "active_balance",
            "withdrawal",
            "allow_auth",
            "blocked",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Логін у ОК"
        self.fields["password_visible"].label = "Пароль від ОК"


class SatelliteAdminForm(forms.ModelForm):
    class Meta:
        model = Satellite
        fields = [
            "uuid",
            "username",
            "block_balance",
            "active_balance",
            "withdrawal",
            "interval",
            "allow_auth",
            "blocked",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Логін у ОК"
        self.fields["password_visible"].label = "Пароль від ОК"
