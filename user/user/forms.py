from dataclasses import fields
from typing import Any

from django import forms
from django.contrib.auth.forms import (
    ReadOnlyPasswordHashField,
    UserChangeForm,
    UsernameField,
)
from django.utils.translation import gettext_lazy as _

from .models import User


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserAdminCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "name", "last_name"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_2 = cleaned_data.get("password_2")
        if password is not None and password != password_2:
            self.add_error("password_2", "Your passwords must match")
        return cleaned_data

    def save(self, commit=True):
        user: User = super().save(commit=False)
        user.is_active = True
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserAdminChangingForm(UserChangeForm):
    def __init__(self, *args: Any, instance=None, **kwargs: Any) -> None:
        self.previous_password = instance.password if instance else ...
        super().__init__(*args, instance=instance, **kwargs)

    class Meta:
        model = User
        fields = "__all__"
        field_classes = {"username": UsernameField}

    def clean_password(self):
        return ""

    def save(self, commit: bool = True) -> Any:
        if self.previous_password is not ...:
            self.instance.password = self.previous_password

        return super().save(commit)
