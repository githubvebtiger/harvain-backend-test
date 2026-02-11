# region				-----External Imports-----
from django import forms

# region				-----Internal Imports-----
from .models import Client
from .phone_utils import format_phone_for_display, parse_phone_for_storage

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class ClientLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class ClientAdminForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["username"].label = "Логін у чистилище"
        self.fields["password_visible"].label = "Пароль у чистилище"


class ClientInlineForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["username", "password_visible", "full_name", "salesman"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
