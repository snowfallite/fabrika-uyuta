"""S2-05: leads in the admin (tech.md, S2-05)."""

from datetime import timedelta

import pytest
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.core.enums import SheetStatus
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
