"""S1-07: outbox worker against the fake sheet (tech.md, 8.4)."""

import logging
import random
import threading
import time
from datetime import timedelta
from typing import Any

import pytest
from django.db import connection
from django.utils import timezone
from hypothesis import given
from hypothesis import strategies as st

from apps.core.enums import SheetStatus
from apps.leads.messenger.fake import FakeMessengerClient
from apps.leads.models import Lead
from apps.leads.retry import backoff_seconds
from apps.leads.sheets.fake import FailureKind, FakeSheetsClient
from apps.leads.sheets.row import validate_row
from apps.leads.tests.factories import make_lead
from apps.leads.worker import Outcome, run_cycle, sync_lead


def rng() -> random.Random:
    return random.Random(7)  # noqa: S311  deterministic jitter in tests


def base(n: int) -> float:
    return float(min(30 * 2 ** (n - 1), 3600))


class MidRandom(random.Random):
    """uniform() at the middle of the jitter range: exposes the base delay."""

    def uniform(self, a: float, b: float) -> float:
        return 1.0


@given(st.integers(1, 60), st.randoms(use_true_random=False))
def test_backoff_stays_in_the_jitter_window(n: int, rnd: random.Random) -> None:
    delay = backoff_seconds(n, rnd)
    assert 0.8 * base(n) <= delay <= 1.2 * base(n)
    assert delay <= 3600 * 1.2


@given(st.integers(1, 59))
def test_backoff_base_never_shrinks(n: int) -> None:
    assert backoff_seconds(n, MidRandom()) <= backoff_seconds(n + 1, MidRandom())


def test_backoff_rejects_attempt_zero() -> None:
    with pytest.raises(ValueError, match="starts at 1"):
        backoff_seconds(0, rng())


@pytest.mark.django_db
def test_ac1_one_cycle_sends_a_pending_lead() -> None:
    lead = make_lead()
    client = FakeSheetsClient()

    assert run_cycle(client, FakeMessengerClient(), rng()) == 1

    rows = client.rows()
    assert len(rows) == 1
    validate_row(rows[0])
    assert rows[0][0] == str(lead.public_id)
    lead.refresh_from_db()
    assert lead.sheet_status == SheetStatus.SENT
    assert lead.sheet_synced_at is not None


@pytest.mark.django_db
def test_ac1_cycle_skips_leads_that_are_not_due() -> None:
    make_lead(sheet_next_attempt_at=timezone.now() + timedelta(minutes=5))
    make_lead(sheet_status=SheetStatus.FAILED)
    client = FakeSheetsClient()
    assert run_cycle(client, FakeMessengerClient(), rng()) == 0
    assert client.rows() == []


@pytest.mark.django_db
def test_ac2_running_the_handler_twice_gives_one_row() -> None:
    lead = make_lead()
    client = FakeSheetsClient()
    now = timezone.now()
    assert sync_lead(lead.pk, client, now, rng()) == Outcome.SENT
    assert sync_lead(lead.pk, client, now, rng()) == Outcome.SKIPPED
    # Even a lead forced back to pending does not get a second row.
    Lead.objects.filter(pk=lead.pk).update(sheet_status=SheetStatus.PENDING, sheet_synced_at=None)
    assert sync_lead(lead.pk, client, now, rng()) == Outcome.SENT
    assert len(client.rows()) == 1


@pytest.mark.django_db
def test_ac2_lost_response_then_retry_gives_one_row() -> None:
    lead = make_lead()
    client = FakeSheetsClient()
    client.lose_response_once()
    now = timezone.now()

    assert sync_lead(lead.pk, client, now, rng()) == Outcome.RETRY
    assert len(client.rows()) == 1
    assert sync_lead(lead.pk, client, now, rng()) == Outcome.SENT

    assert len(client.rows()) == 1
    lead.refresh_from_db()
    assert lead.sheet_status == SheetStatus.SENT


@pytest.mark.django_db
@pytest.mark.parametrize("kind", ["429", "500", "timeout"])
@pytest.mark.parametrize("attempts_before", [0, 3, 9])
def test_ac3_retryable_error_schedules_a_retry(kind: FailureKind, attempts_before: int) -> None:
    lead = make_lead(sheet_attempts=attempts_before)
    client = FakeSheetsClient()
    client.fail_next(kind)
    now = timezone.now()

    assert sync_lead(lead.pk, client, now, rng()) == Outcome.RETRY

    lead.refresh_from_db()
    n = attempts_before + 1
    assert lead.sheet_status == SheetStatus.PENDING
    assert lead.sheet_attempts == n
    earliest = now + timedelta(seconds=0.8 * base(n))
    latest = now + timedelta(seconds=1.2 * base(n))
    assert earliest <= lead.sheet_next_attempt_at <= latest
    assert client.rows() == []


@pytest.mark.django_db
def test_ac3_max_attempts_turn_the_lead_failed(settings: Any) -> None:
    settings.SHEETS_MAX_ATTEMPTS = 3
    lead = make_lead(sheet_alerted_at=timezone.now())
    client = FakeSheetsClient()
    client.fail_next("500", times=3)
    now = timezone.now()

    outcomes = [sync_lead(lead.pk, client, now, rng()) for _ in range(3)]

    assert outcomes == [Outcome.RETRY, Outcome.RETRY, Outcome.FAILED]
    lead.refresh_from_db()
    assert (lead.sheet_status, lead.sheet_attempts) == (SheetStatus.FAILED, 3)
    assert lead.sheet_alerted_at is None


@pytest.mark.django_db
def test_ac4_permanent_error_fails_at_once_without_pii() -> None:
    lead = make_lead(name="Секретов Секрет", phone="+79990000002", comment="личное")
    client = FakeSheetsClient()
    client.fail_next("403")

    assert sync_lead(lead.pk, client, timezone.now(), rng()) == Outcome.FAILED

    lead.refresh_from_db()
    assert (lead.sheet_status, lead.sheet_attempts) == (SheetStatus.FAILED, 1)
    assert "403" in lead.sheet_last_error
    assert "SheetsPermanentError" in lead.sheet_last_error
    for pii in (lead.name, lead.phone, lead.comment):
        assert pii not in lead.sheet_last_error


class SlowFake(FakeSheetsClient):
    """Holds the row lock long enough for a second worker to arrive."""

    def exists(self, lead_id: str) -> bool:
        time.sleep(0.3)
        return super().exists(lead_id)


@pytest.mark.django_db(transaction=True)
def test_ac5_two_workers_on_one_lead_give_one_row() -> None:
    lead = make_lead()
    client = SlowFake()
    barrier = threading.Barrier(2)
    outcomes: list[Outcome] = []

    def work() -> None:
        barrier.wait()
        try:
            outcomes.append(sync_lead(lead.pk, client, timezone.now(), rng()))
        finally:
            connection.close()

    threads = [threading.Thread(target=work) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(outcomes) == sorted([Outcome.SENT, Outcome.SKIPPED])
    assert len(client.rows()) == 1


@pytest.mark.django_db
def test_ac6_formula_text_reaches_the_row_unchanged() -> None:
    make_lead(comment="=1+1")
    client = FakeSheetsClient()
    run_cycle(client, FakeMessengerClient(), rng())
    assert client.rows()[0][6] == "=1+1"


@pytest.mark.django_db
def test_worker_logs_carry_no_pii(caplog: pytest.LogCaptureFixture) -> None:
    lead = make_lead(name="Секретов Секрет", phone="+79990000003", comment="личное")
    client = FakeSheetsClient()
    client.fail_next("500")
    with caplog.at_level(logging.INFO, logger="apps.leads.worker"):
        sync_lead(lead.pk, client, timezone.now(), rng())
        sync_lead(lead.pk, client, timezone.now(), rng())
    assert f"lead={lead.public_id} attempt=1 outcome=retry" in caplog.text
    assert f"lead={lead.public_id} attempt=2 outcome=sent" in caplog.text
    for pii in (lead.name, lead.phone, lead.comment):
        assert pii not in caplog.text


@pytest.mark.django_db
def test_file_backed_fake_survives_a_new_client(tmp_path: Any) -> None:
    make_lead()
    path = tmp_path / "fake-sheet.jsonl"
    run_cycle(FakeSheetsClient(path), FakeMessengerClient(), rng())
    assert len(FakeSheetsClient(path).rows()) == 1
