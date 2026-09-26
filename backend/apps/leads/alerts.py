"""Email alerts about leads stuck on the way to the sheet (tech.md, 8.4). No PII in them."""

import logging
from datetime import UTC, datetime, timedelta
from smtplib import SMTPException

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Max, Q, QuerySet
from django.urls import reverse

from apps.core.enums import SheetStatus
from apps.leads.models import Lead

logger = logging.getLogger(__name__)

WINDOW = timedelta(minutes=30)
SMTP_BACKOFF = timedelta(minutes=5)
STUCK_ATTEMPTS = 7  # about 30 minutes of retries
# A failed transition clears sheet_alerted_at, so the last email time is kept here as well.
LAST_SENT_KEY = "sheets_alerts:last_sent_at"
RETRY_AFTER_KEY = "sheets_alerts:retry_after"


def alert_candidates() -> QuerySet[Lead]:
    stuck = Q(sheet_status=SheetStatus.PENDING, sheet_attempts__gte=STUCK_ATTEMPTS)
    return Lead.objects.filter(
        Q(sheet_status=SheetStatus.FAILED) | stuck, sheet_alerted_at__isnull=True
    ).order_by("created_at")


def check_alerts(now: datetime) -> bool:
    """Send at most one email per window; returns True when an email went out."""
    if not settings.ALERT_EMAIL:
        return False
    retry_after = cache.get(RETRY_AFTER_KEY)
    if retry_after is not None and now.timestamp() < float(retry_after):
        return False
    candidates = list(alert_candidates().values_list("pk", "public_id"))
    if not candidates:
        return False
    last = _last_sent()
    if last is not None and now - last < WINDOW:
        return False
    try:
        send_mail(
            subject=f"Фабрика Уюта: {len(candidates)} заявок не дошли до таблицы",
            message=_body([str(public_id) for _, public_id in candidates]),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ALERT_EMAIL],
        )
    except (SMTPException, OSError) as exc:
        logger.warning("sheets alert email failed: %s", type(exc).__name__)
        cache.set(RETRY_AFTER_KEY, (now + SMTP_BACKOFF).timestamp(), timeout=None)
        return False
    Lead.objects.filter(pk__in=[pk for pk, _ in candidates]).update(sheet_alerted_at=now)
    cache.set(LAST_SENT_KEY, now.timestamp(), timeout=None)
    logger.info("sheets alert sent for %s leads", len(candidates))
    return True


def _last_sent() -> datetime | None:
    in_db = Lead.objects.aggregate(last=Max("sheet_alerted_at"))["last"]
    cached = cache.get(LAST_SENT_KEY)
    in_cache = datetime.fromtimestamp(float(cached), tz=UTC) if cached is not None else None
    return max((t for t in (in_db, in_cache) if t is not None), default=None)


def _body(public_ids: list[str]) -> str:
    link = f"{settings.PUBLIC_SITE_URL}{reverse('admin:leads_lead_changelist')}"
    lines = [
        "Эти заявки не удалось отправить в Google-таблицу. Данные клиентов в письмо не входят.",
        "",
        *public_ids,
        "",
        f"Список заявок в админке: {link}",
    ]
    return "\n".join(lines)
