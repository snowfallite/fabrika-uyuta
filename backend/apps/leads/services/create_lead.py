"""Write side of leads: Postgres first, the worker takes it from there (tech.md, 8.4)."""

from datetime import datetime
from typing import Any

from django.conf import settings

from apps.core.enums import NotifyStatus, SheetStatus
from apps.leads.models import Lead


def create_lead(data: dict[str, Any], now: datetime) -> Lead:
    """Store a validated lead; the phone is already E.164."""
    return Lead.objects.create(
        name=data["name"],
        phone=data["phone"],
        product=data["product"],
        dimensions=data.get("dimensions", ""),
        comment=data.get("comment", ""),
        source_url=data.get("source_url", ""),
        consent_version=settings.CONSENT_VERSION,
        consent_at=now,
        sheet_status=SheetStatus.PENDING,
        sheet_next_attempt_at=now,
        notify_status=NotifyStatus.PENDING,
        notify_next_attempt_at=now,
    )
