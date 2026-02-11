from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from . import models as client_models
from .phone_utils import format_phone_for_display, parse_phone_for_storage


class VerificationInlineForm(forms.ModelForm):
    class Meta:
        model = client_models.Client
        fields = ['email_verified', 'document_verified', 'document_verified_at']


class VerificationInline(admin.StackedInline):
    """Custom inline for verification section"""
    model = client_models.Client
    form = VerificationInlineForm
    verbose_name = "Верифікація документів"
    verbose_name_plural = "Верифікація документів"
    can_delete = False
    max_num = 0
    min_num = 0
    fields = ['email_verified', 'document_verified', 'document_verified_at']
    
    def has_add_permission(self, request, obj=None):
        return False


class ContactInfoInlineForm(forms.ModelForm):
    phone_display = forms.CharField(
        label="Номер телефону",
        required=False,
        help_text="Формат: +380 123456789 або +994 123456789"
    )
    
    class Meta:
        model = client_models.Client
        fields = ['email', 'name', 'last_name', 'country', 'city', 'address', 'born']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Format phone for display
        if self.instance and self.instance.phone:
            self.fields['phone_display'].initial = format_phone_for_display(self.instance.phone)
    
    def save(self, commit=True):
        # Parse phone back to storage format if changed
        phone_display = self.cleaned_data.get('phone_display', '')
        if phone_display:
            self.instance.phone = parse_phone_for_storage(phone_display)
        return super().save(commit=commit)


class ContactInfoInline(admin.StackedInline):
    """Custom inline for contact information section"""
    model = client_models.Client
    form = ContactInfoInlineForm
    verbose_name = "Контактна інформація"
    verbose_name_plural = "Контактна інформація"
    can_delete = False
    max_num = 0
    min_num = 0
    fields = ['email', 'phone_display', 'name', 'last_name', 'country', 'city', 'address', 'born']
    
    def has_add_permission(self, request, obj=None):
        return False