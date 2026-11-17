"""S2-13: the email about a new lead (tech.md, section 24)."""

import random
from datetime import timedelta
from smtplib import SMTPException, SMTPRecipientsRefused
from typing import Any
from unittest import mock
from zoneinfo import ZoneInfo

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from hypothesis import given
from hypothesis import strategies as st

from apps.content.models import SiteSettings
from apps.core.enums import NotifyStatus, ProductKind, SheetStatus
from apps.leads.messenger.fake import FakeMessengerClient
from apps.leads.models import Lead
from apps.leads.notify import (
    NotifyOutcome,
    build_message,
    notify_lead,
    parse_recipients,
    run_notify_batch,
)
from apps.leads.services.create_lead import create_lead
from apps.leads.sheets.fake import FakeSheetsClient
from apps.leads.tests.factories import make_lead
from apps.leads.worker import run_cycle

pytestmark = pytest.mark.django_db
RNG = random.Random(0)  # noqa: S311  jitter only
RECIPIENTS = ["manager@example.ru", "owner@example.ru"]


@pytest.fixture(autouse=True)
def notify_on(settings: Any) -> None:
    settings.PUBLIC_SITE_URL = "https://example.com"
    settings.LEAD_NOTIFY_MAX_ATTEMPTS = 6
    SiteSettings.objects.update_or_create(id=1, defaults={"notify_emails": ", ".join(RECIPIENTS)})


def queued(**overrides: Any) -> Lead:
    return make_lead(notify_status=NotifyStatus.PENDING, **overrides)


def card_url(lead: Lead) -> str:
    return "https://example.com" + reverse("admin:leads_lead_change", args=[lead.pk])


def test_ac1_new_lead_reaches_every_recipient() -> None:
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
    assert lead.notify_status == NotifyStatus.PENDING

    assert run_notify_batch(now, RNG) == 1

    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.to == RECIPIENTS
    assert email.subject == "Фабрика Уюта: новая заявка, Кухни под заказ"
    lead.refresh_from_db()
    assert lead.notify_status == NotifyStatus.SENT
    assert lead.notify_sent_at == now
    assert lead.notify_last_error == ""


def test_ac2_notify_lead_twice_sends_one_email() -> None:
    lead = queued()
    now = timezone.now()

    assert notify_lead(lead.pk, now, RNG) is NotifyOutcome.SENT
    assert notify_lead(lead.pk, now, RNG) is NotifyOutcome.SKIPPED

    assert len(mail.outbox) == 1


def test_ac3_unreachable_smtp_schedules_a_retry() -> None:
    lead = queued()
    now = timezone.now()

    with mock.patch("apps.leads.notify.send_mail", side_effect=SMTPException("down")):
        assert notify_lead(lead.pk, now, RNG) is NotifyOutcome.RETRY

    lead.refresh_from_db()
    assert lead.notify_status == NotifyStatus.PENDING
    assert lead.notify_attempts == 1
    assert now + timedelta(seconds=24) <= lead.notify_next_attempt_at <= now + timedelta(seconds=36)
    assert not mail.outbox


def test_ac3_last_attempt_gives_up(settings: Any) -> None:
    settings.LEAD_NOTIFY_MAX_ATTEMPTS = 2
    lead = queued(notify_attempts=1)

    with mock.patch("apps.leads.notify.send_mail", side_effect=SMTPException("down")):
        assert notify_lead(lead.pk, timezone.now(), RNG) is NotifyOutcome.FAILED

    lead.refresh_from_db()
    assert lead.notify_status == NotifyStatus.FAILED
    assert lead.notify_attempts == 2


def test_ac4_configuration_error_fails_at_once_without_pii() -> None:
    lead = queued(comment="секретное пожелание")
    refused = SMTPRecipientsRefused({"manager@example.ru": (550, b"No such user")})

    with mock.patch("apps.leads.notify.send_mail", side_effect=refused):
        assert notify_lead(lead.pk, timezone.now(), RNG) is NotifyOutcome.FAILED

    lead.refresh_from_db()
    assert lead.notify_status == NotifyStatus.FAILED
    assert lead.notify_attempts == 1
    assert "550" in lead.notify_last_error
    assert "SMTPRecipientsRefused" in lead.notify_last_error
    for secret in (lead.name, lead.phone, lead.comment, "manager@example.ru"):
        assert secret not in lead.notify_last_error


def test_ac5_without_recipients_the_lead_goes_quiet() -> None:
    SiteSettings.objects.filter(id=1).update(notify_emails="")
    lead = queued()

    assert notify_lead(lead.pk, timezone.now(), RNG) is NotifyOutcome.OFF

    lead.refresh_from_db()
    assert lead.notify_status == NotifyStatus.OFF
    assert lead.notify_attempts == 0
    assert not mail.outbox


def test_ac5_leads_from_before_the_feature_stay_quiet() -> None:
    make_lead()  # the migration leaves old rows off

    assert run_notify_batch(timezone.now(), RNG) == 0
    assert not mail.outbox


def test_ac6_body_carries_the_lead_and_the_card_link() -> None:
    lead = queued(
        name="Тестовый Клиент",
        phone="+79991234567",
        dimensions="Стена 3,2 м, высота 2,6 м",
        comment="МДФ, белый, к марту",
        source_url="/catalog/kitchens?utm=vk",
    )

    notify_lead(lead.pk, timezone.now(), RNG)

    email = mail.outbox[0]
    expected = (
        "ФИО: Тестовый Клиент",
        "Телефон: +7 (999) 123-45-67",
        "Что заказать: Кухни под заказ",
        "Размеры: Стена 3,2 м, высота 2,6 м",
        "Комментарий: МДФ, белый, к марту",
        "Источник: /catalog/kitchens?utm=vk",
        card_url(lead),
    )
    for line in expected:
        assert line in email.body
    assert (
        lead.created_at.astimezone(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M")
        in email.body
    )
    for secret in (lead.name, lead.phone, lead.comment):
        assert secret not in email.subject


def test_ac6_empty_fields_leave_no_lines() -> None:
    lead = queued(dimensions="", comment="", source_url="")

    notify_lead(lead.pk, timezone.now(), RNG)

    body = mail.outbox[0].body
    for label in ("Размеры", "Комментарий", "Источник"):
        assert label not in body
    assert ": None" not in body


def test_ac6_log_names_the_lead_by_public_id_only(caplog: pytest.LogCaptureFixture) -> None:
    lead = queued(comment="секретное пожелание")

    with caplog.at_level("INFO", logger="apps.leads.notify"):
        notify_lead(lead.pk, timezone.now(), RNG)

    logged = caplog.text
    assert str(lead.public_id) in logged
    for secret in (lead.name, lead.phone, lead.comment):
        assert secret not in logged


def test_ac9_broken_smtp_does_not_hold_the_sheet() -> None:
    lead = queued()
    client = FakeSheetsClient()

    with mock.patch("apps.leads.notify.send_mail", side_effect=SMTPException("down")):
        run_cycle(client, FakeMessengerClient(), RNG)

    lead.refresh_from_db()
    assert lead.sheet_status == SheetStatus.SENT
    assert lead.notify_status == NotifyStatus.PENDING
    assert len(client.rows()) == 1


def test_recipients_keep_their_order_and_lose_duplicates() -> None:
    raw = " b@example.ru ,a@example.ru\nb@example.ru; "

    assert parse_recipients(raw) == ["b@example.ru", "a@example.ru"]


@given(st.lists(st.text(max_size=20), max_size=6))
def test_parse_recipients_is_idempotent_and_clean(parts: list[str]) -> None:
    once = parse_recipients(",".join(parts))

    assert once == parse_recipients(", ".join(once))
    assert all(item and item == item.strip() for item in once)
    assert len(set(once)) == len(once)


@given(name=st.text(max_size=40), comment=st.text(max_size=40))
def test_build_message_keeps_the_subject_free_of_the_lead(name: str, comment: str) -> None:
    lead = Lead(
        name=name,
        phone="+79991234567",
        product=ProductKind.OFFICE,
        comment=comment,
        created_at=timezone.now(),
    )

    message = build_message(lead, ZoneInfo("Europe/Moscow"), "https://example.com/card/")

    assert message.subject == "Фабрика Уюта: новая заявка, Офисная мебель"
    assert ": None" not in message.body
    assert "https://example.com/card/" in message.body
    if name.strip():
        assert name in message.body
    if not comment.strip():
        assert "Комментарий" not in message.body


def test_ac10_production_without_smtp_keeps_the_lead_and_the_log_clean(
    settings: Any, caplog: pytest.LogCaptureFixture
) -> None:
    settings.APP_ENV = "production"
    settings.EMAIL_HOST = ""
    lead = queued(comment="секретное пожелание")

    with caplog.at_level("INFO", logger="apps.leads.notify"):
        assert notify_lead(lead.pk, timezone.now(), RNG) is NotifyOutcome.RETRY

    assert not mail.outbox
    lead.refresh_from_db()
    assert lead.notify_status == NotifyStatus.PENDING
    assert "SmtpNotConfigured" in lead.notify_last_error
    for secret in (lead.name, lead.phone, lead.comment):
        assert secret not in caplog.text
