from collections.abc import Iterable
from datetime import datetime

from apps.core.enums import NotifyStatus
from apps.leads.models import Lead


def retry_notify(lead_ids: Iterable[int], now: datetime) -> int:
    """failed and off -> pending, the only way back (tech.md, 24.3); other statuses stay put."""
    return Lead.objects.filter(
        pk__in=list(lead_ids), notify_status__in=[NotifyStatus.FAILED, NotifyStatus.OFF]
    ).update(
        notify_status=NotifyStatus.PENDING,
        notify_attempts=0,
        notify_next_attempt_at=now,
        notify_last_error="",
    )
