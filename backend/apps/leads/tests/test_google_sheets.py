"""S2-04: GoogleSheetsClient over REST v4 (tech.md, 8.2) with `responses`, no network."""

import json
from io import StringIO
from pathlib import Path
from typing import Any, cast
from urllib.parse import quote

import pytest
import requests
import responses
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.core.management import call_command
from django.core.management.base import CommandError
from responses import matchers

from apps.leads.sheets.client import SheetsPermanentError, SheetsRetryableError
from apps.leads.sheets.google import GoogleSheetsClient
from apps.leads.sheets.row import HEADERS, SheetRow

SHEET = "sheet-id"
TITLE = "Заявки"
BASE = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET}/values/"
ROW: SheetRow = (
    "8f1d9c1e-0000-4000-8000-000000000001",
    "2026-09-26 10:00",
    "Тестовый Клиент",
    "+79991234567",
    "Шкафы",
    "",
    "=1+1",
    "/",
)


def url(a1: str, suffix: str = "") -> str:
    return BASE + quote(f"'{TITLE}'!{a1}", safe="") + suffix


def client() -> GoogleSheetsClient:
    return GoogleSheetsClient(requests.Session(), SHEET, TITLE)


@responses.activate
def test_ac1_append_sends_one_raw_row() -> None:
    responses.post(
        url("A:H", ":append"),
        match=[
            matchers.query_param_matcher(
                {"valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS"}
            ),
            matchers.json_params_matcher({"values": [list(ROW)]}),
        ],
        json={"updates": {"updatedRows": 1}},
    )
    client().append(ROW)
    body = json.loads(cast(bytes, responses.calls[0].request.body))
    assert len(body["values"]) == 1
    assert len(body["values"][0]) == 8
    assert all(isinstance(cell, str) for cell in body["values"][0])


@pytest.mark.parametrize(
    ("status", "error"),
    [
        (408, SheetsRetryableError),
        (429, SheetsRetryableError),
        (500, SheetsRetryableError),
        (502, SheetsRetryableError),
        (503, SheetsRetryableError),
        (504, SheetsRetryableError),
        (400, SheetsPermanentError),
        (401, SheetsPermanentError),
        (403, SheetsPermanentError),
        (404, SheetsPermanentError),
        (409, SheetsPermanentError),
    ],
)
@responses.activate
def test_ac2_http_errors_are_classified(status: int, error: type[Exception]) -> None:
    responses.post(url("A:H", ":append"), status=status, json={"error": {"code": status}})
    with pytest.raises(error) as exc_info:
        client().append(ROW)
    assert exc_info.value.status == status  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("failure", "status"),
    [(requests.Timeout(), "timeout"), (requests.ConnectionError(), "connection")],
)
@responses.activate
def test_ac2_transport_failures_are_retryable(failure: Exception, status: str) -> None:
    responses.get(url("A:A"), body=failure)
    with pytest.raises(SheetsRetryableError) as exc_info:
        client().exists(ROW[0])
    assert exc_info.value.status == status


@responses.activate
def test_ac3_exists_finds_the_id_in_column_a_after_the_header() -> None:
    responses.get(url("A:A"), json={"values": [["ID"], ["other-id"], [ROW[0]]]})
    assert client().exists(ROW[0]) is True
    assert client().exists("missing-id") is False


@responses.activate
def test_ac3_exists_skips_the_header_and_handles_an_empty_sheet() -> None:
    responses.get(url("A:A"), json={"values": [["ID"]]})
    assert client().exists("ID") is False
    responses.get(url("A:A"), json={"range": f"'{TITLE}'!A1:A1000"})
    assert client().exists(ROW[0]) is False


@pytest.fixture
def google_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("apps.leads.management.commands.sheets_check.get_sheets_client", client)


def run_check() -> str:
    out = StringIO()
    call_command("sheets_check", stdout=out)
    return out.getvalue()


@responses.activate
def test_ac4_sheets_check_passes_on_matching_headers(google_client: None) -> None:
    responses.get(url("A1:H1"), json={"values": [list(HEADERS)]})
    assert "match" in run_check()


@pytest.mark.parametrize(
    ("status", "body", "hint"),
    [
        (200, {"values": [["ID", "Дата", "Имя"]]}, "header"),
        (200, {}, "header"),
        (403, {"error": {"code": 403}}, "403"),
        (400, {"error": {"code": 400}}, "400"),
    ],
)
@responses.activate
def test_ac4_sheets_check_fails_with_a_clear_message(
    google_client: None, status: int, body: dict[str, Any], hint: str
) -> None:
    responses.get(url("A1:H1"), status=status, json=body)
    with pytest.raises(CommandError) as exc_info:
        run_check()
    assert hint in str(exc_info.value)


def test_client_builds_from_a_service_account_file(tmp_path: Path, settings: Any) -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    key_file = tmp_path / "google-sa.json"
    key_file.write_text(
        json.dumps(
            {
                "type": "service_account",
                "client_email": "worker@example.iam.gserviceaccount.com",
                "private_key": pem,
                "private_key_id": "test",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        )
    )
    settings.GOOGLE_SERVICE_ACCOUNT_FILE = key_file
    settings.GOOGLE_SPREADSHEET_ID = SHEET
    settings.GOOGLE_WORKSHEET_TITLE = TITLE
    assert isinstance(GoogleSheetsClient.from_settings(), GoogleSheetsClient)
