"""S1-04 AC4: lead invariants hold in the database."""

import pytest
from django.db import IntegrityError, transaction

from apps.core.enums import SheetStatus
from apps.leads.tests.factories import make_lead

pytestmark = pytest.mark.django_db


def test_ac4_sent_without_synced_at_is_rejected() -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_lead(sheet_status=SheetStatus.SENT, sheet_synced_at=None)


@pytest.mark.parametrize("phone", ["89991234567", "+7 999 123-45-67", "+0123456789", "+7999"])
def test_ac4_non_e164_phone_is_rejected(phone: str) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_lead(phone=phone)


def test_ac4_valid_lead_is_stored() -> None:
    lead = make_lead()
    assert lead.sheet_status == SheetStatus.PENDING
