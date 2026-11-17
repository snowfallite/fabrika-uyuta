"""Message to the MAX group chat: the third outbox of the worker (tech.md, 25.4)."""

import enum
import logging
import random
import threading
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import transaction

from apps.content.models import SiteSettings
from apps.core.enums import NotifyStatus
from apps.leads.messenger.client import (
    MessengerClient,
    MessengerError,
    MessengerPermanentError,
    MessengerRetryableError,
)
from apps.leads.messenger.text import build_keyboard, build_text
from apps.leads.models import Lead
from apps.leads.retry import backoff_seconds

logger = logging.getLogger(__name__)

BATCH_SIZE = 10


class MessengerOutcome(enum.StrEnum):
    SENT = "sent"
    RETRY = "retry"
    FAILED = "failed"
    OFF = "off"
    SKIPPED = "skipped"


def get_chat_id() -> int | None:
    """The chat lives in the admin, so the owner moves it without a deploy (tech.md, 25.1)."""
    chat_id: int | None = (
        SiteSettings.objects.filter(id=1).values_list("max_chat_id", flat=True).first()
    )
    return chat_id


def send_lead(
    lead_id: int, client: MessengerClient, now: datetime, rng: random.Random
) -> MessengerOutcome:
    """Forward one lead to the chat. One queue entry yields at most one message."""
    chat_id = get_chat_id()
    with transaction.atomic():
        lead = Lead.objects.select_for_update(skip_locked=True).filter(pk=lead_id).first()
        if lead is None or lead.max_status != NotifyStatus.PENDING:
            return MessengerOutcome.SKIPPED
        attempt = lead.max_attempts
        if chat_id is None:
            # No chat yet: the lead leaves the queue until the owner retries it.
            lead.max_status = NotifyStatus.OFF
            outcome = MessengerOutcome.OFF
        else:
            attempt += 1
            try:
                client.send(
                    chat_id,
                    build_text(lead, ZoneInfo(settings.SHEETS_TIMEZONE)),
                    build_keyboard(lead),
                )
            except MessengerPermanentError as exc:
                outcome = _fail(lead, exc)
            except MessengerRetryableError as exc:
                outcome = _retry(lead, exc, now, rng)
            except Exception as exc:
                logger.exception("lead=%s max_attempt=%s unexpected error", lead.public_id, attempt)
                outcome = _retry(lead, exc, now, rng)
            else:
                lead.max_status = NotifyStatus.SENT
                lead.max_sent_at = now
                lead.max_last_error = ""
                outcome = MessengerOutcome.SENT
        lead.save(
            update_fields=[
                "max_status",
                "max_attempts",
                "max_next_attempt_at",
                "max_last_error",
                "max_sent_at",
            ]
        )
    logger.info("lead=%s max_attempt=%s outcome=%s", lead.public_id, attempt, outcome)
    return outcome


def run_messenger_batch(
    client: MessengerClient,
    now: datetime,
    rng: random.Random,
    stop: threading.Event | None = None,
) -> int:
    """One pass over leads due for the chat, oldest first; returns how many were picked up."""
    due = (
        Lead.objects.filter(max_status=NotifyStatus.PENDING, max_next_attempt_at__lte=now)
        .order_by("max_next_attempt_at")
        .values_list("id", flat=True)[:BATCH_SIZE]
    )
    picked = 0
    for lead_id in list(due):
        if stop is not None and stop.is_set():
            break
        send_lead(lead_id, client, now, rng)
        picked += 1
    return picked


def _describe(exc: Exception) -> str:
    # HTTP status or MAX error code plus the error class: the body may echo the message text.
    if isinstance(exc, MessengerError):
        return f"{exc.status} {type(exc).__name__}"[:500]
    return type(exc).__name__[:500]


def _fail(lead: Lead, exc: Exception) -> MessengerOutcome:
    lead.max_attempts += 1
    lead.max_last_error = _describe(exc)
    lead.max_status = NotifyStatus.FAILED
    return MessengerOutcome.FAILED


def _retry(lead: Lead, exc: Exception, now: datetime, rng: random.Random) -> MessengerOutcome:
    if lead.max_attempts + 1 >= settings.LEAD_MESSENGER_MAX_ATTEMPTS:
        return _fail(lead, exc)
    lead.max_attempts += 1
    lead.max_last_error = _describe(exc)
    lead.max_next_attempt_at = now + timedelta(seconds=backoff_seconds(lead.max_attempts, rng))
    return MessengerOutcome.RETRY
