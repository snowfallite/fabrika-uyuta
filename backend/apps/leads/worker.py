"""Outbox job sheets.append_lead (tech.md, 8.4): Postgres first, the sheet is a projection."""

import enum
import logging
import random
import signal
import threading
from collections.abc import Callable
from datetime import datetime, timedelta
from types import FrameType
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from apps.core.enums import SheetStatus
from apps.leads.alerts import check_alerts
from apps.leads.models import Lead
from apps.leads.notify import run_notify_batch
from apps.leads.retry import backoff_seconds
from apps.leads.sheets.client import (
    SheetsClient,
    SheetsError,
    SheetsPermanentError,
    SheetsRetryableError,
)
from apps.leads.sheets.row import build_row

logger = logging.getLogger(__name__)

HEARTBEAT_KEY = "sheets_worker:heartbeat"
BATCH_SIZE = 10


class Outcome(enum.StrEnum):
    SENT = "sent"
    RETRY = "retry"
    FAILED = "failed"
    SKIPPED = "skipped"


def sync_lead(lead_id: int, client: SheetsClient, now: datetime, rng: random.Random) -> Outcome:
    """Push one lead to the sheet. Safe to repeat: a lead yields at most one row."""
    with transaction.atomic():
        lead = Lead.objects.select_for_update(skip_locked=True).filter(pk=lead_id).first()
        if lead is None or lead.sheet_status != SheetStatus.PENDING:
            return Outcome.SKIPPED
        attempt = lead.sheet_attempts + 1
        try:
            # A lost response after a successful append leaves the row in place: check first.
            if not client.exists(str(lead.public_id)):
                client.append(build_row(lead, ZoneInfo(settings.SHEETS_TIMEZONE)))
        except SheetsPermanentError as exc:
            outcome = _fail(lead, exc)
        except SheetsRetryableError as exc:
            outcome = _retry(lead, exc, now, rng)
        except Exception as exc:
            logger.exception("lead=%s attempt=%s unexpected error", lead.public_id, attempt)
            outcome = _retry(lead, exc, now, rng)
        else:
            lead.sheet_status = SheetStatus.SENT
            lead.sheet_synced_at = now
            lead.sheet_last_error = ""
            outcome = Outcome.SENT
        lead.save(
            update_fields=[
                "sheet_status",
                "sheet_attempts",
                "sheet_next_attempt_at",
                "sheet_last_error",
                "sheet_synced_at",
                "sheet_alerted_at",
            ]
        )
    logger.info("lead=%s attempt=%s outcome=%s", lead.public_id, attempt, outcome)
    return outcome


def run_cycle(
    client: SheetsClient,
    rng: random.Random,
    stop: threading.Event | None = None,
    now: Callable[[], datetime] = timezone.now,
) -> int:
    """One pass for the sheet, then one for the notifications; returns the sheet leads taken."""
    due = (
        Lead.objects.filter(sheet_status=SheetStatus.PENDING, sheet_next_attempt_at__lte=now())
        .order_by("sheet_next_attempt_at")
        .values_list("id", flat=True)[:BATCH_SIZE]
    )
    picked = 0
    for lead_id in list(due):
        if stop is not None and stop.is_set():
            break
        sync_lead(lead_id, client, now(), rng)
        heartbeat(now())
        picked += 1
    heartbeat(now())
    # Independent queue: an unreachable SMTP never holds up the sheet (tech.md, 24.3).
    run_notify_batch(now(), rng, stop)
    heartbeat(now())
    check_alerts(now())
    return picked


def heartbeat(now: datetime) -> None:
    cache.set(HEARTBEAT_KEY, now.timestamp(), timeout=None)


def run_forever(client: SheetsClient, rng: random.Random) -> None:
    """Poll every SHEETS_POLL_SECONDS; SIGTERM lets the current lead finish, then exits."""
    stop = threading.Event()

    def request_stop(signum: int, frame: FrameType | None) -> None:
        logger.info("stop requested by signal %s", signum)
        stop.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    logger.info("sheets worker started")
    while not stop.is_set():
        run_cycle(client, rng, stop)
        stop.wait(settings.SHEETS_POLL_SECONDS)
    logger.info("sheets worker stopped")


def _describe(exc: Exception) -> str:
    # Status and class only: exception text may echo request data.
    if isinstance(exc, SheetsError):
        return f"{exc.status} {type(exc).__name__}"[:500]
    return type(exc).__name__[:500]


def _fail(lead: Lead, exc: Exception) -> Outcome:
    lead.sheet_attempts += 1
    lead.sheet_last_error = _describe(exc)
    lead.sheet_status = SheetStatus.FAILED
    lead.sheet_alerted_at = None
    return Outcome.FAILED


def _retry(lead: Lead, exc: Exception, now: datetime, rng: random.Random) -> Outcome:
    if lead.sheet_attempts + 1 >= settings.SHEETS_MAX_ATTEMPTS:
        return _fail(lead, exc)
    lead.sheet_attempts += 1
    lead.sheet_last_error = _describe(exc)
    lead.sheet_next_attempt_at = now + timedelta(seconds=backoff_seconds(lead.sheet_attempts, rng))
    return Outcome.RETRY
