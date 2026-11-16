"""S2-13: notification delivery as a state machine (tech.md, 24.3).

Operations: SMTP works, SMTP is down, the configuration is wrong, the owner retries from the
admin, the recipients change and time passes. Invariants: only the 24.3 transitions, every sent
notification has notify_sent_at, and one queue entry yields at most one email.
"""

import random
from datetime import datetime, timedelta
from smtplib import SMTPException, SMTPRecipientsRefused
from typing import Any
from unittest import mock

import pytest
from django.core import mail
from django.utils import timezone
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule

from apps.content.models import SiteSettings
from apps.core.enums import NotifyStatus
from apps.leads.models import Lead
from apps.leads.notify import notify_lead
from apps.leads.services.notify_retry import retry_notify
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
RECIPIENT = "manager@example.ru"


class NotifyLifecycle(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()
        self.now: datetime = timezone.now()
        self.rng = random.Random(0)  # noqa: S311  jitter only
        self.ids: list[int] = []
        self.status: dict[int, str] = {}
        # Emails sent per lead against the queue entries that justify them.
        self.emails: dict[int, int] = {}
        self.entries: dict[int, int] = {}

    @initialize()
    def fresh_leads(self) -> None:
        Lead.objects.all().delete()
        mail.outbox.clear()
        SiteSettings.objects.update_or_create(id=1, defaults={"notify_emails": RECIPIENT})
        for number in range(LEADS):
            lead = make_lead(phone=f"+7999000020{number}", notify_status=NotifyStatus.PENDING)
            self.ids.append(lead.pk)
            self.status[lead.pk] = lead.notify_status
            self.emails[lead.pk] = 0
            self.entries[lead.pk] = 1

    def _deliver(self, index: int, error: Exception | None) -> None:
        lead_id = self.ids[index % LEADS]
        before = len(mail.outbox)
        if error is None:
            notify_lead(lead_id, self.now, self.rng)
        else:
            with mock.patch("apps.leads.notify.send_mail", side_effect=error):
                notify_lead(lead_id, self.now, self.rng)
        if len(mail.outbox) > before:
            self.emails[lead_id] += 1

    @rule(index=st.integers(0, LEADS - 1))
    def smtp_works(self, index: int) -> None:
        self._deliver(index, None)

    @rule(index=st.integers(0, LEADS - 1))
    def smtp_is_down(self, index: int) -> None:
        self._deliver(index, SMTPException("connection refused"))

    @rule(index=st.integers(0, LEADS - 1))
    def configuration_is_wrong(self, index: int) -> None:
        self._deliver(index, SMTPRecipientsRefused({RECIPIENT: (550, b"no such user")}))

    @rule(index=st.integers(0, LEADS - 1))
    def admin_retry(self, index: int) -> None:
        lead_id = self.ids[index % LEADS]
        if retry_notify([lead_id], self.now):
            self.entries[lead_id] += 1

    @rule(filled=st.booleans())
    def recipients_change(self, filled: bool) -> None:
        SiteSettings.objects.filter(id=1).update(notify_emails=RECIPIENT if filled else "")

    @rule(minutes=st.integers(1, 90))
    def time_passes(self, minutes: int) -> None:
        self.now += timedelta(minutes=minutes)

    @invariant()
    def only_allowed_transitions(self) -> None:
        for lead in Lead.objects.filter(pk__in=self.ids):
            previous = self.status[lead.pk]
            assert (previous, lead.notify_status) in ALLOWED, (previous, lead.notify_status)
            self.status[lead.pk] = lead.notify_status

    @invariant()
    def sent_notifications_have_sent_at(self) -> None:
        assert not Lead.objects.filter(
            notify_status=NotifyStatus.SENT, notify_sent_at__isnull=True
        ).exists()

    @invariant()
    def one_queue_entry_yields_one_email(self) -> None:
        for lead_id in self.ids:
            assert self.emails[lead_id] <= self.entries[lead_id], "lead emailed twice per entry"


NotifyLifecycle.TestCase.settings = hypothesis_settings(stateful_step_count=25, deadline=None)


@pytest.mark.django_db
def test_notify_lifecycle(settings: Any) -> None:
    settings.PUBLIC_SITE_URL = "https://example.com"
    # Four attempts keep the machine moving between pending and failed inside a run.
    settings.LEAD_NOTIFY_MAX_ATTEMPTS = 4
    NotifyLifecycle.TestCase().runTest()
