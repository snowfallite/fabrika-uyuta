"""S2-05: alerts about leads that do not reach the sheet (tech.md, 8.4)."""

import logging
from datetime import timedelta
from smtplib import SMTPException
from typing import Any
from unittest import mock

import pytest
from django.core import mail
from django.utils import timezone

from apps.core.enums import SheetStatus
from apps.leads.alerts import check_alerts
from apps.leads.models import Lead
from apps.leads.tests.factories import make_lead

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def alerts_on(settings: Any) -> None:
    settings.ALERT_EMAIL = "ops@example.com"
    settings.PUBLIC_SITE_URL = "https://example.com"


def failed(**overrides: Any) -> Lead:
    return make_lead(
        sheet_status=SheetStatus.FAILED,
        sheet_attempts=12,
        sheet_last_error="403 SheetsPermanentError",
        **overrides,
    )


def pii(lead: Lead) -> list[str]:
    return [lead.name, lead.phone, lead.comment or "never-empty-marker"]


def test_ac3_one_email_lists_candidates_without_pii() -> None:
    now = timezone.now()
    stuck = make_lead(sheet_attempts=7, phone="+79990000011", comment="секрет")
    dead = failed(name="Второй Клиент", phone="+79990000012")
    calm = make_lead(sheet_attempts=6, phone="+79990000013")

    assert check_alerts(now) is True

    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.to == ["ops@example.com"]
    assert str(stuck.public_id) in email.body and str(dead.public_id) in email.body
    assert str(calm.public_id) not in email.body
    assert "https://example.com/admin/leads/lead/" in email.body
    for lead in (stuck, dead, calm):
        for value in pii(lead):
            assert value not in email.body and value not in email.subject
    stuck.refresh_from_db()
    dead.refresh_from_db()
    calm.refresh_from_db()
    assert stuck.sheet_alerted_at == now and dead.sheet_alerted_at == now
    assert calm.sheet_alerted_at is None


def test_ac3_nothing_to_report_sends_nothing() -> None:
    make_lead()
    assert check_alerts(timezone.now()) is False
    assert mail.outbox == []


def test_ac3_empty_alert_email_disables_alerts(settings: Any) -> None:
    settings.ALERT_EMAIL = ""
    failed()
    assert check_alerts(timezone.now()) is False
    assert mail.outbox == []


def test_ac4_new_candidate_waits_for_the_window_and_old_ones_stay_quiet() -> None:
    start = timezone.now()
    first = failed()
    assert check_alerts(start) is True

    second = failed(phone="+79990000021")
    assert check_alerts(start + timedelta(minutes=10)) is False
    assert check_alerts(start + timedelta(minutes=29)) is False
    assert check_alerts(start + timedelta(minutes=30)) is True

    assert len(mail.outbox) == 2
    assert str(second.public_id) in mail.outbox[1].body
    assert str(first.public_id) not in mail.outbox[1].body
    assert check_alerts(start + timedelta(hours=5)) is False


def test_ac4_a_new_failed_transition_is_reported_again() -> None:
    start = timezone.now()
    lead = make_lead(sheet_attempts=7)
    assert check_alerts(start) is True
    # pending -> failed clears sheet_alerted_at (8.4): a new transition, a new alert.
    Lead.objects.filter(pk=lead.pk).update(sheet_status=SheetStatus.FAILED, sheet_alerted_at=None)
    assert check_alerts(start + timedelta(minutes=5)) is False  # still inside the window
    assert check_alerts(start + timedelta(minutes=31)) is True
    assert str(lead.public_id) in mail.outbox[1].body


def test_ac5_smtp_error_logs_without_pii_and_backs_off(caplog: pytest.LogCaptureFixture) -> None:
    start = timezone.now()
    lead = failed(name="Скрытое Имя", phone="+79990000031")
    with (
        mock.patch("apps.leads.alerts.send_mail", side_effect=SMTPException("boom")) as send,
        caplog.at_level(logging.WARNING, logger="apps.leads.alerts"),
    ):
        assert check_alerts(start) is False
        assert check_alerts(start + timedelta(minutes=4)) is False
        assert send.call_count == 1

    lead.refresh_from_db()
    assert lead.sheet_alerted_at is None
    assert "SMTPException" in caplog.text
    for value in pii(lead):
        assert value not in caplog.text

    assert check_alerts(start + timedelta(minutes=5)) is True
    assert len(mail.outbox) == 1
