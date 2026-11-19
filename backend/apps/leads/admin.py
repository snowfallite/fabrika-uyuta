from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone

from apps.leads.models import Lead
from apps.leads.product import product_label
from apps.leads.services.max_retry import retry_max
from apps.leads.services.notify_retry import retry_notify
from apps.leads.services.sheet_retry import retry_sheet_sync


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """Read-only list for managers (tech.md, S2-05); the sheet is where they work."""

    list_display = [
        "created_at",
        "name",
        "phone",
        "product_title",
        "sheet_status",
        "sheet_attempts",
        "notify_status",
        "max_status",
    ]
    # v15: the kinds are categories, so the filter lists the titles leads were sent with.
    list_filter = ["sheet_status", "notify_status", "max_status", "product_label", "created_at"]
    search_fields = ["name", "phone"]
    date_hierarchy = "created_at"
    actions = ["retry_sheet_sync", "retry_notify", "retry_max"]
    readonly_fields = [field.name for field in Lead._meta.fields]

    @admin.display(description="Что заказать", ordering="product_label")
    def product_title(self, obj: Lead) -> str:
        return product_label(obj)

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

    def has_retry_notify_permission(self, request: HttpRequest) -> bool:
        return bool(request.user.has_perm("leads.retry_notify"))

    @admin.action(description="Повторить уведомление", permissions=["retry_notify"])
    def retry_notify(self, request: HttpRequest, queryset: QuerySet[Lead]) -> None:
        count = retry_notify(queryset.values_list("pk", flat=True), timezone.now())
        self.message_user(request, f"Повторное уведомление запланировано: {count}.")

    def has_retry_max_permission(self, request: HttpRequest) -> bool:
        return bool(request.user.has_perm("leads.retry_max"))

    @admin.action(description="Повторить отправку в MAX", permissions=["retry_max"])
    def retry_max(self, request: HttpRequest, queryset: QuerySet[Lead]) -> None:
        count = retry_max(queryset.values_list("pk", flat=True), timezone.now())
        self.message_user(request, f"Повторная отправка в MAX запланирована: {count}.")
