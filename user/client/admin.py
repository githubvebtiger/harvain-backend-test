from django import contrib, http
from django.contrib import admin
from django.db import models

from bets.admin import BetClientInlineAdmin
from finance.admin import TransactionClientInlineAdmin

from ..satellite.admin import SatelliteClientInlineAdmin
from ..user import admin as user_admin
from ..user.admin import RequisitesInline
from . import forms as client_forms
from . import models as client_models
from .phone_utils import format_phone_for_display
from .admin_inlines import ContactInfoInline


class ClientPasswordsInlineAdmin(contrib.admin.StackedInline):
    model = client_models.ClientPasswords
    fields = ["old_password", "new_password", "created_at"]
    readonly_fields = ["old_password", "new_password", "created_at"]
    can_delete = False
    max_num = 0
    extra = 0

    def get_queryset(self, request: http.HttpRequest):
        queryset = super().get_queryset(request=request)
        last = queryset.last()
        if last:
            last_three = queryset.all().order_by("-id").filter(id__gt=last.id - 3)
        else:
            last_three = queryset
        return last_three


@contrib.admin.register(client_models.Client)
class ClientAdmin(contrib.admin.ModelAdmin):
    list_display = [
        "full_name",
        "salesman",
        "formatted_phone",
        "satellites_filter_link",
        "is_active",
        "shoulder",
        "growth_rate",
        "commission",
    ]
    list_filter = ["salesman", "is_active"]
    form = client_forms.ClientAdminForm
    
    @contrib.admin.display(description="Номер телефону")
    def formatted_phone(self, obj):
        """Display phone number with proper country code format"""
        return format_phone_for_display(obj.phone) if obj.phone else '-'
    fieldsets = [
        (
            "Загальні",
            {
                "fields": [
                    "username",
                    "password_visible",
                    "full_name",
                    "salesman",
                    "total_balance",
                    "is_active",
                    "shoulder",
                    "growth_rate",
                    "commission",
                ]
            },
        ),
        (
            "Верифікація",
            {
                "fields": [
                    "email_verified",
                    "document_verified",
                    "document_verified_at",
                ]
            },
        ),
    ]
    
    @contrib.admin.display(description="Статус верифікації", ordering="verify_status")
    def verify_status_display(self, obj):
        status = obj.verify_status
        colors = {
            "green": "#28a745",
            "yellow": "#ffc107", 
            "red": "#dc3545"
        }
        from django.utils.safestring import mark_safe
        return mark_safe(f'<span style="color: {colors.get(status, "#000")}; font-weight: bold;">●</span> {status.upper()}')
    
    def save_model(self, request, obj, form, change):
        # Auto-set document_verified_at when manually verifying
        if change and 'document_verified' in form.changed_data:
            if obj.document_verified and not obj.document_verified_at:
                from django.utils import timezone
                obj.document_verified_at = timezone.now()
            elif not obj.document_verified:
                obj.document_verified_at = None
        super().save_model(request, obj, form, change)
    
    @contrib.admin.action(description="Верифікувати документи вибраних клієнтів")
    def verify_documents(self, request, queryset):
        from django.utils import timezone
        count = 0
        for client in queryset:
            client.document_verified = True
            client.document_verified_at = timezone.now()
            client.save()
            count += 1
        self.message_user(request, f"Документи верифіковано для {count} клієнтів.")
    
    @contrib.admin.action(description="Скасувати верифікацію документів")
    def unverify_documents(self, request, queryset):
        count = 0
        for client in queryset:
            client.document_verified = False
            client.document_verified_at = None
            client.save()
            count += 1
        self.message_user(request, f"Верифікацію скасовано для {count} клієнтів.")
    
    @contrib.admin.action(description="Верифікувати email вибраних клієнтів")
    def verify_emails(self, request, queryset):
        count = 0
        for client in queryset:
            client.email_verified = True
            client.save()
            count += 1
        self.message_user(request, f"Email верифіковано для {count} клієнтів.")
    
    actions = [verify_documents, unverify_documents, verify_emails]
    inlines = [
        SatelliteClientInlineAdmin,     # Сателіти
        BetClientInlineAdmin,           # Трейдс  
        TransactionClientInlineAdmin,   # Транзакції
        RequisitesInline,               # Реквізити
        ContactInfoInline,              # Контактна інформація
        user_admin.UserEntrancesInline, # Історія входів
        ClientPasswordsInlineAdmin,     # Паролі клієнта
    ]

    def get_queryset(self, request: http.HttpRequest) -> models.QuerySet:
        queryset = (
            super(ClientAdmin, self)
            .get_queryset(request=request)
            .prefetch_related("entrances")
            .select_related("salesman")
        )

        return queryset


class ClientInlineAdmin(contrib.admin.StackedInline):
    form = client_forms.ClientInlineForm
    model = client_models.Client
    fields = ["username", "password_visible", "full_name", "salesman"]


@admin.register(client_models.SupportTicket)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "account_number", "subject")


@admin.register(client_models.PricingPlan)
class CustomPlanAdmin(admin.ModelAdmin):
    list_display = ("full_name", "total_price")


@admin.register(client_models.Payment)
class CustomPaymentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "total_price", "user")
