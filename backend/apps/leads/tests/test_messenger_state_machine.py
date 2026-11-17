"""S2-14: chat delivery as a state machine (tech.md, 25.4).

Operations: MAX answers, MAX fails for a moment, MAX refuses for good, the owner retries from the
admin, the chat is set or cleared and time passes. Invariants: only the 25.4 transitions, every
forwarded lead has max_sent_at, and one queue entry yields at most one message.
"""

import random
from datetime import datetime, timedelta
from typing import Any

import pytest
from django.utils import timezone
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule

from apps.content.models import SiteSettings
from apps.core.enums import NotifyStatus
from apps.leads.messenger.fake import FailureKind, FakeMessengerClient
from apps.leads.messenger.outbox import send_lead
from apps.leads.models import Lead
from apps.leads.services.max_retry import retry_max
from apps.leads.tests.factories import make_lead

ALLOWED = {
    (NotifyStatus.PENDING, NotifyStatus.SENT),
    (NotifyStatus.PENDING, NotifyStatus.PENDING),
    (NotifyStatus.PENDING, NotifyStatus.FAILED),
    (NotifyStatus.PENDING, NotifyStatus.OFF),
    (NotifyStatus.FAILED, NotifyStatus.PENDING),
    (NotifyStatus.OFF, NotifyStatus.PENDING),
    (NotifyStatus.SENT, NotifyStatus.SENT),
    (NotifyStatus.FAILED, NotifyStatus.FAILED),
    (NotifyStatus.OFF, NotifyStatus.OFF),
}
LEADS = 3
CHAT_ID = -12307927


class MessengerLifecycle(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()
        self.now: datetime = timezone.now()
        self.rng = random.Random(0)  # noqa: S311  jitter only
        self.chat = FakeMessengerClient()
        self.ids: list[int] = []
        self.status: dict[int, str] = {}
        # Messages posted per lead against the queue entries that justify them.
        self.posted: dict[int, int] = {}
        self.entries: dict[int, int] = {}

    @initialize()
    def fresh_leads(self) -> None:
        Lead.objects.all().delete()
        SiteSettings.objects.update_or_create(id=1, defaults={"max_chat_id": CHAT_ID})
        for number in range(LEADS):
            lead = make_lead(phone=f"+7999000030{number}", max_status=NotifyStatus.PENDING)
            self.ids.append(lead.pk)
            self.status[lead.pk] = lead.max_status
            self.posted[lead.pk] = 0
            self.entries[lead.pk] = 1

    def _deliver(self, index: int, failure: FailureKind | None) -> None:
        lead_id = self.ids[index % LEADS]
        before = len(self.chat.messages())
        if failure is not None:
            self.chat.fail_next(failure)
        send_lead(lead_id, self.chat, self.now, self.rng)
        if len(self.chat.messages()) > before:
            self.posted[lead_id] += 1

    @rule(index=st.integers(0, LEADS - 1))
    def max_answers(self, index: int) -> None:
        self._deliver(index, None)

    @rule(index=st.integers(0, LEADS - 1), kind=st.sampled_from(["429", "500", "timeout"]))
    def max_fails_for_a_moment(self, index: int, kind: FailureKind) -> None:
        self._deliver(index, kind)

    @rule(index=st.integers(0, LEADS - 1), kind=st.sampled_from(["403", "success_false"]))
    def max_refuses_for_good(self, index: int, kind: FailureKind) -> None:
        self._deliver(index, kind)

    @rule(index=st.integers(0, LEADS - 1))
    def admin_retry(self, index: int) -> None:
        lead_id = self.ids[index % LEADS]
        if retry_max([lead_id], self.now):
            self.entries[lead_id] += 1

    @rule(filled=st.booleans())
    def chat_changes(self, filled: bool) -> None:
        SiteSettings.objects.filter(id=1).update(max_chat_id=CHAT_ID if filled else None)

    @rule(minutes=st.integers(1, 90))
    def time_passes(self, minutes: int) -> None:
        self.now += timedelta(minutes=minutes)

    @invariant()
    def only_allowed_transitions(self) -> None:
        for lead in Lead.objects.filter(pk__in=self.ids):
            previous = self.status[lead.pk]
            assert (previous, lead.max_status) in ALLOWED, (previous, lead.max_status)
            self.status[lead.pk] = lead.max_status

    @invariant()
    def forwarded_leads_have_sent_at(self) -> None:
        assert not Lead.objects.filter(
            max_status=NotifyStatus.SENT, max_sent_at__isnull=True
        ).exists()

    @invariant()
    def one_queue_entry_yields_one_message(self) -> None:
        for lead_id in self.ids:
            assert self.posted[lead_id] <= self.entries[lead_id], "lead posted twice per entry"


MessengerLifecycle.TestCase.settings = hypothesis_settings(stateful_step_count=25, deadline=None)


@pytest.mark.django_db
def test_messenger_lifecycle(settings: Any) -> None:
    # Four attempts keep the machine moving between pending and failed inside a run.
    settings.LEAD_MESSENGER_MAX_ATTEMPTS = 4
    MessengerLifecycle.TestCase().runTest()
