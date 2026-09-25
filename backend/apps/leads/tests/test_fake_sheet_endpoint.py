"""GET /api/v1/test/fake-sheet/ serves E2E only (tech.md, section 7)."""

from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from django.test import Client

from apps.leads.sheets.fake import FakeSheetsClient
from apps.leads.sheets.row import build_row
from apps.leads.tests.factories import make_lead

pytestmark = pytest.mark.django_db
URL = "/api/v1/test/fake-sheet/"


@pytest.fixture
def sheet(tmp_path: Path, settings: Any) -> Path:
    settings.SHEETS_FAKE_PATH = tmp_path / "fake-sheet.jsonl"
    settings.SHEETS_BACKEND = "fake"
    return Path(settings.SHEETS_FAKE_PATH)


def token(settings: Any) -> dict[str, str]:
    return {"X-Internal-Token": settings.INTERNAL_API_TOKEN}


def test_returns_rows_when_enabled(client: Client, sheet: Path, settings: Any) -> None:
    settings.ENABLE_TEST_ENDPOINTS = True
    row = build_row(make_lead(), ZoneInfo("Europe/Moscow"))
    FakeSheetsClient(sheet).append(row)
    response = client.get(URL, headers=token(settings))
    assert response.status_code == 200
    assert response.json() == {"rows": [list(row)]}


def test_is_404_when_disabled(client: Client, sheet: Path, settings: Any) -> None:
    settings.ENABLE_TEST_ENDPOINTS = False
    assert client.get(URL, headers=token(settings)).status_code == 404


def test_needs_the_token(client: Client, sheet: Path, settings: Any) -> None:
    settings.ENABLE_TEST_ENDPOINTS = True
    assert client.get(URL).status_code == 403
