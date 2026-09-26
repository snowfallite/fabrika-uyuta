from collections.abc import Iterable
from datetime import datetime

from apps.core.enums import SheetStatus
from apps.leads.models import Lead


def retry_sheet_sync(lead_ids: Iterable[int], now: datetime) -> int:
    """failed -> pending, the only way back (tech.md, 8.4); other statuses stay as they are."""
    return Lead.objects.filter(pk__in=list(lead_ids), sheet_status=SheetStatus.FAILED).update(
        sheet_status=SheetStatus.PENDING,
        sheet_attempts=0,
        sheet_next_attempt_at=now,
        sheet_last_error="",
        sheet_alerted_at=None,
    )
