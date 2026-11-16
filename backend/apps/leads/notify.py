"""Email about a new lead: the second outbox of the worker (tech.md, section 24)."""

import enum
import logging
import random
import re
import threading
from datetime import datetime, timedelta
from smtplib import (
    SMTPAuthenticationError,
    SMTPException,
    SMTPNotSupportedError,
    SMTPRecipientsRefused,
    SMTPSenderRefused,
)
from typing import NamedTuple
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse

from apps.content.models import SiteSettings
from apps.core.enums import NotifyStatus, ProductKind
from apps.core.phone import format_phone_display
from apps.leads.models import Lead
from apps.leads.retry import backoff_seconds

logger = logging.getLogger(__name__)

BATCH_SIZE = 10
SEPARATORS = re.compile(r"[,;\n\r]+")
# A wrong address, sender or password repeats the same failure, so these do not get a retry.
PERMANENT_ERRORS = (
    SMTPRecipientsRefused,
    SMTPSenderRefused,
    SMTPAuthenticationError,
    SMTPNotSupportedError,
)


class NotifyOutcome(enum.StrEnum):
    SENT = "sent"
    RETRY = "retry"
    FAILED = "failed"
    OFF = "off"
    SKIPPED = "skipped"


class LeadMessage(NamedTuple):
    subject: str
    body: str


def parse_recipients(raw: str) -> list[str]:
    """Addresses from the admin field: comma, semicolon or newline apart, order kept."""
    unique: dict[str, None] = {}
    for part in SEPARATORS.split(raw):
        address = part.strip()
        if address:
            unique.setdefault(address, None)
    return list(unique)


def get_recipients() -> list[str]:
    raw = SiteSettings.objects.filter(id=1).values_list("notify_emails", flat=True).first()
    return parse_recipients(raw or "")


def card_url(lead: Lead) -> str:
    return f"{settings.PUBLIC_SITE_URL}{reverse('admin:leads_lead_change', args=[lead.pk])}"


def build_message(lead: Lead, tz: ZoneInfo, url: str) -> LeadMessage:
    """Subject without PII, body with the lead itself (tech.md, 24.2)."""
    label = ProductKind(lead.product).label
    rows = (
        ("Дата", lead.created_at.astimezone(tz).strftime("%Y-%m-%d %H:%M")),
        ("ФИО", lead.name),
        ("Телефон", format_phone_display(lead.phone)),
        ("Что заказать", label),
        ("Размеры", lead.dimensions),
        ("Комментарий", lead.comment),
        ("Источник", lead.source_url),
    )
    lines = [f"{name}: {value}" for name, value in rows if value]
    lines += ["", f"Карточка в админке: {url}"]
    return LeadMessage(subject=f"Фабрика Уюта: новая заявка, {label}", body="\n".join(lines))


def notify_lead(lead_id: int, now: datetime, rng: random.Random) -> NotifyOutcome:
    """Email one lead to the managers. One queue entry yields at most one email."""
    recipients = get_recipients()
    with transaction.atomic():
        lead = Lead.objects.select_for_update(skip_locked=True).filter(pk=lead_id).first()
        if lead is None or lead.notify_status != NotifyStatus.PENDING:
            return NotifyOutcome.SKIPPED
        attempt = lead.notify_attempts
        if not recipients:
            # Nobody to write to: the lead leaves the queue until the owner retries it.
            lead.notify_status = NotifyStatus.OFF
            outcome = NotifyOutcome.OFF
        else:
            attempt += 1
            message = build_message(lead, ZoneInfo(settings.SHEETS_TIMEZONE), card_url(lead))
            try:
                send_mail(
                    subject=message.subject,
                    message=message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipients,
                )
            except PERMANENT_ERRORS as exc:
                outcome = _fail(lead, exc)
            except (SMTPException, OSError) as exc:
                outcome = _retry(lead, exc, now, rng)
            except Exception as exc:
                logger.exception(
                    "lead=%s notify_attempt=%s unexpected error", lead.public_id, attempt
                )
                outcome = _retry(lead, exc, now, rng)
            else:
                lead.notify_status = NotifyStatus.SENT
                lead.notify_sent_at = now
                lead.notify_last_error = ""
                outcome = NotifyOutcome.SENT
        lead.save(
            update_fields=[
                "notify_status",
                "notify_attempts",
                "notify_next_attempt_at",
                "notify_last_error",
                "notify_sent_at",
            ]
        )
    logger.info("lead=%s notify_attempt=%s outcome=%s", lead.public_id, attempt, outcome)
    return outcome


def run_notify_batch(now: datetime, rng: random.Random, stop: threading.Event | None = None) -> int:
    """One pass over leads due for an email, oldest first; returns how many were picked up."""
    due = (
        Lead.objects.filter(notify_status=NotifyStatus.PENDING, notify_next_attempt_at__lte=now)
        .order_by("notify_next_attempt_at")
        .values_list("id", flat=True)[:BATCH_SIZE]
    )
    picked = 0
    for lead_id in list(due):
        if stop is not None and stop.is_set():
            break
        notify_lead(lead_id, now, rng)
        picked += 1
    return picked


def _describe(exc: Exception) -> str:
    # SMTP code and error class only: the message may echo an address or request data.
    code = getattr(exc, "smtp_code", None)
    if code is None and isinstance(exc, SMTPRecipientsRefused):
        codes = [status for status, _ in exc.recipients.values()]
        code = min(codes) if codes else None
    name = type(exc).__name__
    return (f"{code} {name}" if code is not None else name)[:500]


def _fail(lead: Lead, exc: Exception) -> NotifyOutcome:
    lead.notify_attempts += 1
    lead.notify_last_error = _describe(exc)
    lead.notify_status = NotifyStatus.FAILED
    return NotifyOutcome.FAILED


def _retry(lead: Lead, exc: Exception, now: datetime, rng: random.Random) -> NotifyOutcome:
    if lead.notify_attempts + 1 >= settings.LEAD_NOTIFY_MAX_ATTEMPTS:
        return _fail(lead, exc)
    lead.notify_attempts += 1
    lead.notify_last_error = _describe(exc)
    delay = backoff_seconds(lead.notify_attempts, rng)
    lead.notify_next_attempt_at = now + timedelta(seconds=delay)
    return NotifyOutcome.RETRY
