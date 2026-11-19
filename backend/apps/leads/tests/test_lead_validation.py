"""S2-02: validation texts, cleanup, honeypot, throttling, source_url (tech.md, 7 and 12)."""

import json
import uuid
from pathlib import Path
from typing import Any

import pytest
from django.conf import settings as django_settings
from django.test import Client

from apps.leads.api.serializers import (
    COMMENT_TOO_LONG,
    CONSENT_REQUIRED,
    DIMENSIONS_TOO_LONG,
    NAME_REQUIRED,
    NAME_TOO_LONG,
    NAME_TOO_SHORT,
    PHONE_INVALID,
    PHONE_REQUIRED,
    PRODUCT_REQUIRED,
)
from apps.leads.models import Lead
from apps.leads.tests.factories import make_categories
from apps.leads.tests.test_create_lead_api import post, valid_body

pytestmark = pytest.mark.django_db
TEXTS_12_1 = {
    NAME_REQUIRED,
    NAME_TOO_SHORT,
    NAME_TOO_LONG,
    PHONE_REQUIRED,
    PHONE_INVALID,
    PRODUCT_REQUIRED,
    DIMENSIONS_TOO_LONG,
    COMMENT_TOO_LONG,
    CONSENT_REQUIRED,
}
PHONE_CASES: list[dict[str, Any]] = json.loads(
    (Path(django_settings.BASE_DIR).parent / "contracts/fixtures/phone-cases.json").read_text(
        "utf-8"
    )
)


@pytest.fixture(autouse=True)
def generous_throttle(settings: Any) -> None:
    settings.LEAD_THROTTLE_RATE = "1000/hour"


@pytest.fixture(autouse=True)
def categories() -> None:
    """Since v15 the kind is a category slug, so the categories have to exist (tech.md, 7)."""
    make_categories()


@pytest.mark.parametrize("case", PHONE_CASES, ids=[c["input"] or "<empty>" for c in PHONE_CASES])
def test_ac1_phone_vectors_through_the_api(
    client: Client, settings: Any, case: dict[str, Any]
) -> None:
    response = post(client, settings, valid_body(phone=case["input"]))
    if case["e164"]:
        assert response.status_code == 201
        assert Lead.objects.get().phone == case["e164"]
    else:
        assert response.status_code == 400
        # 12.1: an empty phone has its own text, every other bad value gets PHONE_INVALID.
        expected = PHONE_REQUIRED if case["input"] == "" else PHONE_INVALID
        assert response.json() == {"phone": [expected]}
        assert not Lead.objects.exists()


@pytest.mark.parametrize("consent", [False, None, "yes", "missing"])
def test_ac2_consent_is_required(client: Client, settings: Any, consent: Any) -> None:
    body = valid_body(consent=consent)
    if consent == "missing":
        body.pop("consent")
    response = post(client, settings, body)
    assert response.status_code == 400
    assert response.json() == {"consent": [CONSENT_REQUIRED]}
    assert not Lead.objects.exists()


def test_ac3_name_and_texts_are_cleaned(client: Client, settings: Any) -> None:
    response = post(
        client,
        settings,
        valid_body(
            name="  Иван \t  Петров\x00 ",
            dimensions="  3 м\x07 x 2 м\r\n",
            comment="\x1bстрока 1\r\n\tстрока 2  ",
        ),
    )
    assert response.status_code == 201
    lead = Lead.objects.get()
    assert lead.name == "Иван Петров"
    assert lead.dimensions == "3 м x 2 м"
    assert lead.comment == "строка 1\n\tстрока 2"


@pytest.mark.parametrize(
    ("overrides", "field", "text"),
    [
        ({"name": ""}, "name", NAME_REQUIRED),
        ({"name": "   "}, "name", NAME_REQUIRED),
        ({"name": "12345"}, "name", NAME_REQUIRED),
        ({"name": "Я"}, "name", NAME_TOO_SHORT),
        ({"name": "Я" * 121}, "name", NAME_TOO_LONG),
        ({"name": None}, "name", NAME_REQUIRED),
        ({"name": 42}, "name", NAME_REQUIRED),
        ({"phone": ""}, "phone", PHONE_REQUIRED),
        ({"phone": "9" * 33}, "phone", PHONE_INVALID),
        ({"product": ""}, "product", PRODUCT_REQUIRED),
        ({"product": "spaceship"}, "product", PRODUCT_REQUIRED),
        ({"product": None}, "product", PRODUCT_REQUIRED),
        ({"dimensions": "x" * 301}, "dimensions", DIMENSIONS_TOO_LONG),
        ({"dimensions": ["x"]}, "dimensions", DIMENSIONS_TOO_LONG),
        ({"comment": "x" * 2001}, "comment", COMMENT_TOO_LONG),
        ({"comment": None}, "comment", COMMENT_TOO_LONG),
    ],
)
def test_ac3_errors_use_only_texts_from_12_1(
    client: Client, settings: Any, overrides: dict[str, Any], field: str, text: str
) -> None:
    response = post(client, settings, valid_body(**overrides))
    assert response.status_code == 400
    assert response.json() == {field: [text]}


def test_ac3_several_errors_at_once_stay_in_12_1(client: Client, settings: Any) -> None:
    body = {"name": "1", "phone": "abc", "product": "?", "consent": False}
    response = post(client, settings, body)
    assert response.status_code == 400
    errors = response.json()
    assert set(errors) == {"name", "phone", "product", "consent"}
    assert {message for messages in errors.values() for message in messages} <= TEXTS_12_1


def test_ac4_honeypot_answers_201_and_stores_nothing(client: Client, settings: Any) -> None:
    response = post(client, settings, valid_body(website="https://spam.example"))
    assert response.status_code == 201
    assert uuid.UUID(response.json()["id"]).version == 4
    assert not Lead.objects.exists()


def test_ac4_honeypot_wins_even_over_invalid_fields(client: Client, settings: Any) -> None:
    response = post(client, settings, {"website": "x", "name": ""})
    assert response.status_code == 201
    assert not Lead.objects.exists()


def test_ac5_sixth_request_in_an_hour_is_429_per_ip(client: Client, settings: Any) -> None:
    settings.LEAD_THROTTLE_RATE = "5/hour"
    statuses = [
        post(client, settings, valid_body(), ip="198.51.100.1").status_code for _ in range(6)
    ]
    assert statuses == [201] * 5 + [429]
    assert post(client, settings, valid_body(), ip="198.51.100.2").status_code == 201
    assert Lead.objects.count() == 6


def test_ac5_throttle_counts_honeypot_and_invalid_requests_too(
    client: Client, settings: Any
) -> None:
    settings.LEAD_THROTTLE_RATE = "2/hour"
    post(client, settings, valid_body(website="bot"), ip="198.51.100.3")
    post(client, settings, valid_body(name=""), ip="198.51.100.3")
    assert post(client, settings, valid_body(), ip="198.51.100.3").status_code == 429


@pytest.mark.parametrize(
    ("source_url", "stored"),
    [
        ("https://evil.example/catalog/kitchens?utm=1#top", "/catalog/kitchens?utm=1"),
        ("/lead?product=office", "/lead?product=office"),
        ("", ""),
        ("/" + "a" * 700, "/" + "a" * 499),
    ],
)
def test_ac6_source_url_keeps_path_and_query_cut_to_500(
    client: Client, settings: Any, source_url: str, stored: str
) -> None:
    assert post(client, settings, valid_body(source_url=source_url)).status_code == 201
    assert Lead.objects.get().source_url == stored
