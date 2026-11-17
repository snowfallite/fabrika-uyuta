from collections.abc import Iterable
from datetime import datetime

from apps.core.enums import NotifyStatus
from apps.leads.models import Lead


def retry_max(lead_ids: Iterable[int], now: datetime) -> int:
    """failed and off -> pending, the only way back (tech.md, 25.4); other statuses stay put."""
    return Lead.objects.filter(
        pk__in=list(lead_ids), max_status__in=[NotifyStatus.FAILED, NotifyStatus.OFF]
    ).update(
        max_status=NotifyStatus.PENDING,
        max_attempts=0,
        max_next_attempt_at=now,
        max_last_error="",
    )
