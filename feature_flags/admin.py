from django.contrib import admin
from .models import FeatureToggle

@admin.register(FeatureToggle)
class FeatureToggleAdmin(admin.ModelAdmin):
    list_display = (
        'download_enabled',
        'print_enabled',
        'email_enabled',
        'whatsapp_enabled',
        'password_protection_enabled',
    )