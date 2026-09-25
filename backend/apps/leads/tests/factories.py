from typing import Any

from django.utils import timezone

from apps.core.enums import ProductKind
from apps.leads.models import Lead


def make_lead(**overrides: Any) -> Lead:
    """Fictitious lead data only (tech.md, 13.1)."""
    fields: dict[str, Any] = {
        "name": "Тестовый Клиент",
        "phone": "+79990000001",
        "product": ProductKind.KITCHENS,
        "consent_version": "2026-09-25",
        "consent_at": timezone.now(),
    }
    return Lead.objects.create(**(fields | overrides))
