"""S2-05: lead delivery and alerts as a state machine (tech.md, 8.4).

Operations: worker success, retryable error, permanent error, admin retry, alert check and
time passing. Invariants: only the 8.4 transitions, every sent lead has sheet_synced_at, at most
one email per 30 minutes, and no lead lands in two emails without a new transition between them.
"""

import random
from datetime import datetime, timedelta
from typing import Any

import pytest
from django.core import mail
from django.core.cache import cache
from django.utils import timezone
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule

from apps.core.enums import SheetStatus
from apps.leads.alerts import check_alerts
from apps.leads.models import Lead
from apps.leads.services.sheet_retry import retry_sheet_sync
from apps.leads.sheets.fake import FailureKind, FakeSheetsClient
from apps.leads.tests.factories import make_lead
from apps.leads.worker import sync_lead

ALLOWED = {
    (SheetStatus.PENDING, SheetStatus.SENT),
    (SheetStatus.PENDING, SheetStatus.PENDING),
    (SheetStatus.PENDING, SheetStatus.FAILED),
    (SheetStatus.FAILED, SheetStatus.PENDING),
    (SheetStatus.SENT, SheetStatus.SENT),
    (SheetStatus.FAILED, SheetStatus.FAILED),
}
LEADS = 3


class LeadLifecycle(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()
        self.now: datetime = timezone.now()
        self.rng = random.Random(0)  # noqa: S311  jitter only
        self.client = FakeSheetsClient()
        self.ids: list[int] = []
        self.status: dict[int, str] = {}
        self.attempts: dict[int, int] = {}
        # Lead ids already emailed since their last transition.
        self.reported: set[int] = set()
        self.email_times: list[datetime] = []

    @initialize()
    def fresh_leads(self) -> None:
        Lead.objects.all().delete()
        cache.clear()
        mail.outbox.clear()
        for number in range(LEADS):
            lead = make_lead(phone=f"+7999000010{number}")
            self.ids.append(lead.pk)
            self.status[lead.pk] = lead.sheet_status
            self.attempts[lead.pk] = lead.sheet_attempts

    def _sync(self, index: int, failure: FailureKind | None) -> None:
        lead_id = self.ids[index % LEADS]
        # The worker skips leads that are not pending; an injected failure would then linger.
        pending = Lead.objects.filter(pk=lead_id, sheet_status=SheetStatus.PENDING).exists()
        if failure and pending:
            self.client.fail_next(failure)
        sync_lead(lead_id, self.client, self.now, self.rng)

    @rule(index=st.integers(0, LEADS - 1))
    def worker_success(self, index: int) -> None:
        self._sync(index, None)

    @rule(index=st.integers(0, LEADS - 1), kind=st.sampled_from(["429", "500", "timeout"]))
    def worker_retryable(self, index: int, kind: FailureKind) -> None:
        self._sync(index, kind)

    @rule(index=st.integers(0, LEADS - 1))
    def worker_permanent(self, index: int) -> None:
        self._sync(index, "403")

    @rule(index=st.integers(0, LEADS - 1))
    def admin_retry(self, index: int) -> None:
        retry_sheet_sync([self.ids[index % LEADS]], self.now)

    @rule()
    def alert_check(self) -> None:
        before = len(mail.outbox)
        check_alerts(self.now)
        if len(mail.outbox) > before:
            body = mail.outbox[-1].body
            emailed = {pk for pk in self.ids if str(self._public_id(pk)) in body}
            assert emailed.isdisjoint(self.reported), "lead emailed twice without a transition"
            self.reported |= emailed
            self.email_times.append(self.now)

    @rule(minutes=st.integers(1, 90))
    def time_passes(self, minutes: int) -> None:
        self.now += timedelta(minutes=minutes)

    def _public_id(self, pk: int) -> Any:
        return Lead.objects.values_list("public_id", flat=True).get(pk=pk)

    @invariant()
    def only_allowed_transitions(self) -> None:
        if not self.ids:
            return
        for lead in Lead.objects.filter(pk__in=self.ids):
            previous = self.status[lead.pk]
            assert (previous, lead.sheet_status) in ALLOWED, (previous, lead.sheet_status)
            changed = previous != lead.sheet_status or (
                lead.sheet_status == SheetStatus.PENDING
                and lead.sheet_attempts < self.attempts[lead.pk]
            )
            if changed:
                # A new transition makes the lead reportable again.
                self.reported.discard(lead.pk)
            self.status[lead.pk] = lead.sheet_status
            self.attempts[lead.pk] = lead.sheet_attempts

    @invariant()
    def sent_leads_have_synced_at(self) -> None:
        assert not Lead.objects.filter(
            sheet_status=SheetStatus.SENT, sheet_synced_at__isnull=True
        ).exists()

    @invariant()
    def emails_are_at_least_30_minutes_apart(self) -> None:
        for earlier, later in zip(self.email_times, self.email_times[1:], strict=False):
            assert later - earlier >= timedelta(minutes=30)


LeadLifecycle.TestCase.settings = hypothesis_settings(stateful_step_count=25, deadline=None)


@pytest.mark.django_db
def test_lead_lifecycle(settings: Any) -> None:
    settings.ALERT_EMAIL = "ops@example.com"
    # Nine attempts leave room for "pending with 7+ attempts" alerts before a lead fails.
    settings.SHEETS_MAX_ATTEMPTS = 9
    LeadLifecycle.TestCase().runTest()
