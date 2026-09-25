"""POST /api/v1/leads/ (S2-01, S2-02)."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from datetime import timedelta
from typing import Any

import pytest
from django.test import Client
from django.utils import timezone

from apps.core.enums import SheetStatus
from apps.leads.api.serializers import PHONE_INVALID
from apps.leads.models import Lead

pytestmark = pytest.mark.django_db
URL = "/api/v1/leads/"
MaxQueries = Callable[[int], AbstractContextManager[Any]]


def valid_body(**overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "name": "Тестовый Клиент",
        "phone": "8 (999) 123-45-67",
        "product": "wardrobes",
        "dimensions": "2,4 x 0,6 м",
        "comment": "Светлый дуб",
        "consent": True,
        "website": "",
        "source_url": "/catalog/wardrobes",
    }
    return body | overrides


def post(client: Client, settings: Any, body: dict[str, Any], ip: str = "203.0.113.10") -> Any:
    return client.post(
        URL,
        body,
        content_type="application/json",
        headers={"X-Internal-Token": settings.INTERNAL_API_TOKEN, "X-Client-IP": ip},
    )


def test_ac3_valid_lead_is_saved_and_returns_its_public_id(client: Client, settings: Any) -> None:
    before = timezone.now()
    response = post(client, settings, valid_body())
    after = timezone.now()

    assert response.status_code == 201
    lead = Lead.objects.get()
    assert response.json() == {"id": str(lead.public_id)}
    assert lead.phone == "+79991234567"
    assert (lead.name, lead.product) == ("Тестовый Клиент", "wardrobes")
    assert (lead.dimensions, lead.comment) == ("2,4 x 0,6 м", "Светлый дуб")
    assert lead.consent_version == settings.CONSENT_VERSION
    assert before <= lead.consent_at <= after
    assert lead.sheet_status == SheetStatus.PENDING
    assert lead.sheet_attempts == 0
    assert lead.sheet_next_attempt_at <= after + timedelta(seconds=1)


def test_ac3_invalid_phone_is_a_400_not_a_500(client: Client, settings: Any) -> None:
    response = post(client, settings, valid_body(phone="12345"))
    assert response.status_code == 400
    assert response.json() == {"phone": [PHONE_INVALID]}
    assert not Lead.objects.exists()


def test_create_lead_query_count(
    client: Client, settings: Any, django_assert_max_num_queries: MaxQueries
) -> None:
    # Throttle bookkeeping lives in the database cache, the insert is one query.
    with django_assert_max_num_queries(6):
        assert post(client, settings, valid_body()).status_code == 201
