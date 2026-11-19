"""S2-05: leads in the admin (tech.md, S2-05)."""

from datetime import timedelta

import pytest
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.core.enums import NotifyStatus, SheetStatus
from apps.leads.models import Lead
from apps.leads.tests.factories import make_lead

pytestmark = pytest.mark.django_db
CHANGELIST = "admin:leads_lead_changelist"


def staff_in(group: str) -> Client:
    call_command("sync_reference_data")
    user = User.objects.create_user(f"{group}-user", is_staff=True)
    user.groups.add(Group.objects.get(name=group))
    client = Client()
    client.force_login(user)
    return client


def superuser() -> Client:
    client = Client()
    client.force_login(User.objects.create_superuser("owner", "owner@example.com", "x"))
    return client


def retry(client: Client, *leads: Lead) -> None:
    response = client.post(
        reverse(CHANGELIST),
        {"action": "retry_sheet_sync", "_selected_action": [lead.pk for lead in leads]},
    )
    assert response.status_code == 302


def test_ac1_leads_group_reads_and_retries() -> None:
    client = staff_in("Заявки")
    lead = make_lead(sheet_status=SheetStatus.FAILED, sheet_attempts=12)

    changelist = client.get(reverse(CHANGELIST))
    assert changelist.status_code == 200
    assert "Тестовый Клиент" in changelist.content.decode()
    card = client.get(reverse("admin:leads_lead_change", args=[lead.pk]))
    assert card.status_code == 200
    assert 'name="_save"' not in card.content.decode()

    retry(client, lead)
    lead.refresh_from_db()
    assert lead.sheet_status == SheetStatus.PENDING


def test_ac1_content_group_does_not_see_leads() -> None:
    client = staff_in("Контент")
    assert client.get(reverse(CHANGELIST)).status_code == 403


def test_ac2_retry_resets_only_failed_leads() -> None:
    now = timezone.now()
    failed = make_lead(
        sheet_status=SheetStatus.FAILED,
        sheet_attempts=12,
        sheet_last_error="403 SheetsPermanentError",
        sheet_alerted_at=now,
        sheet_next_attempt_at=now - timedelta(days=1),
    )
    pending = make_lead(sheet_attempts=3, sheet_alerted_at=now)
    sent = make_lead(sheet_status=SheetStatus.SENT, sheet_synced_at=now)

    retry(superuser(), failed, pending, sent)

    failed.refresh_from_db()
    assert failed.sheet_status == SheetStatus.PENDING
    assert (failed.sheet_attempts, failed.sheet_last_error, failed.sheet_alerted_at) == (
        0,
        "",
        None,
    )
    assert failed.sheet_next_attempt_at >= now
    pending.refresh_from_db()
    assert (pending.sheet_status, pending.sheet_attempts) == (SheetStatus.PENDING, 3)
    assert pending.sheet_alerted_at == now
    sent.refresh_from_db()
    assert sent.sheet_status == SheetStatus.SENT


def test_ac6_nobody_adds_or_edits_and_only_superusers_delete() -> None:
    lead = make_lead()
    staff = staff_in("Заявки")
    owner = superuser()
    change_url = reverse("admin:leads_lead_change", args=[lead.pk])
    delete_url = reverse("admin:leads_lead_delete", args=[lead.pk])

    for client in (staff, owner):
        assert client.get(reverse("admin:leads_lead_add")).status_code == 403
        client.post(change_url, {"name": "Другое Имя"})
        lead.refresh_from_db()
        assert lead.name == "Тестовый Клиент"
    assert staff.post(delete_url, {"post": "yes"}).status_code == 403
    assert Lead.objects.filter(pk=lead.pk).exists()
    assert owner.post(delete_url, {"post": "yes"}).status_code == 302
    assert not Lead.objects.filter(pk=lead.pk).exists()


def test_ac11_the_changelist_shows_the_kind_label_and_filters_by_it() -> None:
    client = staff_in("Заявки")
    make_lead(product="kids-rooms", product_label="Детские комнаты")
    make_lead(product="office", product_label="")  # a lead from before v15

    page = client.get(reverse(CHANGELIST)).content.decode()

    assert "Детские комнаты" in page
    assert "Офисная мебель" in page  # the enum still labels the old lead
    assert "kids-rooms" not in page

    filtered = client.get(reverse(CHANGELIST), {"product_label__exact": "Детские комнаты"})

    assert "Детские комнаты" in filtered.content.decode()
    assert "Офисная мебель" not in filtered.content.decode()


def notify_retry(client: Client, *leads: Lead) -> None:
    response = client.post(
        reverse(CHANGELIST),
        {"action": "retry_notify", "_selected_action": [lead.pk for lead in leads]},
    )
    assert response.status_code == 302


def test_ac7_leads_group_retries_a_notification() -> None:
    client = staff_in("Заявки")
    lead = make_lead(
        notify_status=NotifyStatus.FAILED,
        notify_attempts=6,
        notify_last_error="550 SMTPRecipientsRefused",
    )

    notify_retry(client, lead)

    lead.refresh_from_db()
    assert lead.notify_status == NotifyStatus.PENDING
    assert (lead.notify_attempts, lead.notify_last_error) == (0, "")


def test_ac7_notify_retry_touches_only_failed_and_off_leads() -> None:
    now = timezone.now()
    failed = make_lead(notify_status=NotifyStatus.FAILED, notify_attempts=6)
    off = make_lead(notify_status=NotifyStatus.OFF)
    pending = make_lead(notify_status=NotifyStatus.PENDING, notify_attempts=2)
    sent = make_lead(notify_status=NotifyStatus.SENT, notify_sent_at=now)

    notify_retry(superuser(), failed, off, pending, sent)

    for lead in (failed, off):
        lead.refresh_from_db()
        assert lead.notify_status == NotifyStatus.PENDING
        assert lead.notify_attempts == 0
        assert lead.notify_next_attempt_at >= now
    pending.refresh_from_db()
    assert (pending.notify_status, pending.notify_attempts) == (NotifyStatus.PENDING, 2)
    sent.refresh_from_db()
    assert sent.notify_status == NotifyStatus.SENT


def max_retry(client: Client, *leads: Lead) -> None:
    response = client.post(
        reverse(CHANGELIST),
        {"action": "retry_max", "_selected_action": [lead.pk for lead in leads]},
    )
    assert response.status_code == 302


def test_ac7_leads_group_retries_a_chat_message() -> None:
    client = staff_in("Заявки")
    lead = make_lead(
        max_status=NotifyStatus.FAILED,
        max_attempts=6,
        max_last_error="403 MessengerPermanentError",
    )

    max_retry(client, lead)

    lead.refresh_from_db()
    assert lead.max_status == NotifyStatus.PENDING
    assert (lead.max_attempts, lead.max_last_error) == (0, "")


def test_ac7_max_retry_touches_only_failed_and_off_leads() -> None:
    now = timezone.now()
    failed = make_lead(max_status=NotifyStatus.FAILED, max_attempts=6)
    off = make_lead(max_status=NotifyStatus.OFF)
    sent = make_lead(max_status=NotifyStatus.SENT, max_sent_at=now)

    max_retry(staff_in("Заявки"), failed, off, sent)

    for lead in (failed, off):
        lead.refresh_from_db()
        assert lead.max_status == NotifyStatus.PENDING
    sent.refresh_from_db()
    assert sent.max_status == NotifyStatus.SENT
