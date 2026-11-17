"""S2-14: forwarding a lead to the MAX group chat (tech.md, section 25)."""

import logging
import random
from datetime import timedelta
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from django.utils import timezone
from hypothesis import given
from hypothesis import strategies as st

from apps.content.models import SiteSettings
from apps.core.enums import NotifyStatus, ProductKind, SheetStatus
from apps.leads.messenger.fake import FailureKind, FakeMessengerClient
from apps.leads.messenger.outbox import MessengerOutcome, run_messenger_batch, send_lead
from apps.leads.messenger.text import MAX_LENGTH, ContractViolation, build_text, validate_text
from apps.leads.models import Lead
from apps.leads.services.create_lead import create_lead
from apps.leads.services.max_retry import retry_max
from apps.leads.sheets.fake import FakeSheetsClient
from apps.leads.tests.factories import make_lead
from apps.leads.worker import run_cycle

pytestmark = pytest.mark.django_db
RNG = random.Random(0)  # noqa: S311  jitter only
CHAT_ID = -12307927
TZ = ZoneInfo("Europe/Moscow")
FIELD = st.text(alphabet=st.characters(exclude_characters=":\n"), max_size=120)


@pytest.fixture(autouse=True)
def chat_on(settings: Any) -> None:
    settings.LEAD_MESSENGER_MAX_ATTEMPTS = 6
    settings.SHEETS_TIMEZONE = "Europe/Moscow"
    SiteSettings.objects.update_or_create(
        id=1, defaults={"max_chat_id": CHAT_ID, "notify_emails": "manager@example.test"}
    )


def queued(**overrides: Any) -> Lead:
    return make_lead(**({"max_status": NotifyStatus.PENDING} | overrides))


def base(n: int) -> float:
    return float(min(30 * 2 ** (n - 1), 3600))


def test_ac1_new_lead_reaches_the_chat() -> None:
    now = timezone.now()
    lead = create_lead(
        {
            "name": "Тестовый Клиент",
            "phone": "+79991234567",
            "product": ProductKind.KITCHENS,
            "dimensions": "Стена 3,2 м, высота 2,6 м",
            "comment": "МДФ, белый",
            "source_url": "/catalog/kitchens",
        },
        now,
    )
    assert lead.max_status == NotifyStatus.PENDING
    chat = FakeMessengerClient()

    assert run_messenger_batch(chat, now, RNG) == 1

    lead.refresh_from_db()
    assert len(chat.messages()) == 1
    message = chat.messages()[0]
    assert message["chat_id"] == CHAT_ID
    assert message["text"] == (
        "<b>Новая заявка: Кухни под заказ</b>\n"
        "\n"
        f"<b>Дата:</b> {lead.created_at.astimezone(TZ):%Y-%m-%d %H:%M}\n"
        "<b>ФИО:</b> Тестовый Клиент\n"
        "<b>Телефон:</b> +7 (999) 123-45-67\n"
        "<b>Размеры:</b> Стена 3,2 м, высота 2,6 м\n"
        "<b>Комментарий:</b> МДФ, белый\n"
        "<b>Источник:</b> /catalog/kitchens"
    )
    assert lead.max_status == NotifyStatus.SENT
    assert lead.max_sent_at == now
    assert lead.max_last_error == ""


def test_ac2_send_lead_twice_posts_one_message() -> None:
    lead = queued()
    chat = FakeMessengerClient()
    now = timezone.now()

    assert send_lead(lead.pk, chat, now, RNG) is MessengerOutcome.SENT
    assert send_lead(lead.pk, chat, now, RNG) is MessengerOutcome.SKIPPED

    assert len(chat.messages()) == 1


def test_ac2_a_lost_response_costs_one_duplicate_and_no_more() -> None:
    """MAX has no cheap "already sent" question, so the contract pays with a visible repeat."""
    lead = queued()
    chat = FakeMessengerClient()
    chat.lose_response_once()
    now = timezone.now()

    assert send_lead(lead.pk, chat, now, RNG) is MessengerOutcome.RETRY
    assert send_lead(lead.pk, chat, now + timedelta(hours=1), RNG) is MessengerOutcome.SENT

    assert len(chat.messages()) == 2
    lead.refresh_from_db()
    assert lead.max_status == NotifyStatus.SENT


@pytest.mark.parametrize("kind", ["429", "500", "timeout"])
def test_ac3_a_server_side_failure_schedules_a_retry(kind: FailureKind) -> None:
    lead = queued()
    chat = FakeMessengerClient()
    chat.fail_next(kind)
    now = timezone.now()

    assert send_lead(lead.pk, chat, now, RNG) is MessengerOutcome.RETRY

    lead.refresh_from_db()
    assert lead.max_status == NotifyStatus.PENDING
    assert lead.max_attempts == 1
    assert chat.messages() == []
    delay = (lead.max_next_attempt_at - now).total_seconds()
    assert 0.8 * base(1) <= delay <= 1.2 * base(1)


def test_ac3_retries_stop_at_the_attempt_limit(settings: Any) -> None:
    settings.LEAD_MESSENGER_MAX_ATTEMPTS = 3
    lead = queued()
    chat = FakeMessengerClient()
    chat.fail_next("500", times=3)
    now = timezone.now()

    for _ in range(3):
        send_lead(lead.pk, chat, now, RNG)
        Lead.objects.filter(pk=lead.pk).update(max_next_attempt_at=now)

    lead.refresh_from_db()
    assert lead.max_status == NotifyStatus.FAILED
    assert lead.max_attempts == 3


@pytest.mark.parametrize(("kind", "marker"), [("403", "403"), ("success_false", "chat.denied")])
def test_ac4_a_permanent_failure_stops_the_lead_at_once(kind: FailureKind, marker: str) -> None:
    lead = queued(name="Секретное Имя", phone="+79995554433", comment="тайна клиента")
    chat = FakeMessengerClient()
    chat.fail_next(kind)

    assert send_lead(lead.pk, chat, timezone.now(), RNG) is MessengerOutcome.FAILED

    lead.refresh_from_db()
    assert lead.max_status == NotifyStatus.FAILED
    assert lead.max_attempts == 1
    assert marker in lead.max_last_error
    assert "MessengerPermanentError" in lead.max_last_error
    for secret in ("Секретное Имя", "+79995554433", "тайна клиента"):
        assert secret not in lead.max_last_error


def test_ac5_an_empty_chat_takes_the_lead_out_of_the_queue() -> None:
    SiteSettings.objects.filter(id=1).update(max_chat_id=None)
    lead = queued()
    chat = FakeMessengerClient()

    assert send_lead(lead.pk, chat, timezone.now(), RNG) is MessengerOutcome.OFF

    lead.refresh_from_db()
    assert lead.max_status == NotifyStatus.OFF
    assert lead.max_attempts == 0
    assert chat.messages() == []


def test_ac5_a_lead_that_predates_the_feature_stays_quiet() -> None:
    make_lead()
    chat = FakeMessengerClient()

    assert run_messenger_batch(chat, timezone.now(), RNG) == 0

    assert chat.messages() == []


def test_ac6_empty_fields_leave_no_rows_and_no_admin_link() -> None:
    lead = queued(dimensions="", comment="", source_url="")
    chat = FakeMessengerClient()

    send_lead(lead.pk, chat, timezone.now(), RNG)

    text = str(chat.messages()[0]["text"])
    for label in ("Размеры", "Комментарий", "Источник"):
        assert label not in text
    assert "<b>ФИО:</b> Тестовый Клиент" in text
    # The admin path is a secret and the chat is wider than the mailing list (tech.md, 25.3).
    assert "http" not in text


def test_ac6_logs_carry_no_pii(caplog: pytest.LogCaptureFixture) -> None:
    lead = queued(name="Секретное Имя", phone="+79995554433", comment="тайна клиента")

    with caplog.at_level(logging.INFO, logger="apps.leads.messenger.outbox"):
        send_lead(lead.pk, FakeMessengerClient(), timezone.now(), RNG)

    logged = caplog.text
    assert str(lead.public_id) in logged
    for secret in ("Секретное Имя", "+79995554433", "тайна клиента"):
        assert secret not in logged


def test_ac7_retry_lifts_failed_and_off_only() -> None:
    now = timezone.now()
    failed = queued(max_status=NotifyStatus.FAILED, max_attempts=4, max_last_error="403 x")
    off = queued(max_status=NotifyStatus.OFF)
    sent = queued(max_status=NotifyStatus.SENT, max_sent_at=now)
    pending = queued()

    assert retry_max([failed.pk, off.pk, sent.pk, pending.pk], now) == 2

    for lead in (failed, off):
        lead.refresh_from_db()
        assert lead.max_status == NotifyStatus.PENDING
        assert lead.max_attempts == 0
        assert lead.max_next_attempt_at == now
        assert lead.max_last_error == ""
    sent.refresh_from_db()
    assert sent.max_status == NotifyStatus.SENT
    pending.refresh_from_db()
    assert pending.max_status == NotifyStatus.PENDING


def test_ac10_a_broken_max_holds_up_neither_the_sheet_nor_the_email() -> None:
    lead = queued(notify_status=NotifyStatus.PENDING)
    sheet = FakeSheetsClient()
    chat = FakeMessengerClient()
    chat.fail_next("500")

    run_cycle(sheet, chat, RNG)

    lead.refresh_from_db()
    assert lead.sheet_status == SheetStatus.SENT
    assert lead.notify_status == NotifyStatus.SENT
    assert lead.max_status == NotifyStatus.PENDING
    assert len(sheet.rows()) == 1


def test_a_multiline_comment_keeps_its_line_breaks() -> None:
    lead = queued(comment="первая строка\nвторая строка")
    chat = FakeMessengerClient()

    send_lead(lead.pk, chat, timezone.now(), RNG)

    assert "<b>Комментарий:</b> первая строка\nвторая строка" in str(chat.messages()[0]["text"])


def test_validate_text_guards_the_max_limit() -> None:
    validate_text("x" * MAX_LENGTH)
    with pytest.raises(ContractViolation, match="longer than"):
        validate_text("x" * (MAX_LENGTH + 1))
    with pytest.raises(ContractViolation, match="empty"):
        validate_text("   ")


@given(name=FIELD, dimensions=FIELD, comment=FIELD, source=FIELD)
def test_build_text_fits_the_limit_and_skips_empty_fields(
    name: str, dimensions: str, comment: str, source: str
) -> None:
    lead = Lead(
        name=name,
        phone="+79991234567",
        product=ProductKind.OFFICE,
        dimensions=dimensions,
        comment=comment,
        source_url=source,
        created_at=timezone.now(),
    )

    text = build_text(lead, TZ)

    validate_text(text)
    assert len(text) <= MAX_LENGTH
    assert text.startswith("<b>Новая заявка: Офисная мебель</b>")
    assert ": None" not in text
    for value, label in ((dimensions, "Размеры"), (comment, "Комментарий"), (source, "Источник")):
        assert (f"<b>{label}:</b> " in text) is bool(value)
