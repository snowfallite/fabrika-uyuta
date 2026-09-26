from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone

from apps.leads.models import Lead
from apps.leads.services.sheet_retry import retry_sheet_sync


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """Read-only list for managers (tech.md, S2-05); the sheet is where they work."""

    list_display = [
        "created_at",
        "name",
        "phone",
        "product",
        "sheet_status",
        "sheet_attempts",
    ]
    list_filter = ["sheet_status", "product", "created_at"]
    search_fields = ["name", "phone"]
    date_hierarchy = "created_at"
    actions = ["retry_sheet_sync"]
    readonly_fields = [field.name for field in Lead._meta.fields]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: object = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: object = None) -> bool:
        return bool(request.user.is_superuser)

    def has_retry_sheet_sync_permission(self, request: HttpRequest) -> bool:
        return bool(request.user.has_perm("leads.retry_sheet_sync"))

    @admin.action(description="Повторить отправку", permissions=["retry_sheet_sync"])
    def retry_sheet_sync(self, request: HttpRequest, queryset: QuerySet[Lead]) -> None:
        count = retry_sheet_sync(queryset.values_list("pk", flat=True), timezone.now())
        self.message_user(request, f"Повторная отправка запланирована: {count}.")
