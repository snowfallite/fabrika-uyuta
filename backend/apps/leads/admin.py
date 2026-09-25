from django.contrib import admin

from apps.leads.models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["created_at", "name", "phone", "product", "sheet_status", "sheet_attempts"]
