"""Google Sheets REST v4 transport (tech.md, 8.2): plain HTTP with google-auth, no wrappers."""

from typing import Any, Self
from urllib.parse import quote

import requests
from django.conf import settings
from google.auth.exceptions import GoogleAuthError, TransportError
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from apps.leads.sheets.client import SheetsPermanentError, SheetsRetryableError
from apps.leads.sheets.row import SheetRow

SCOPE = "https://www.googleapis.com/auth/spreadsheets"
API = "https://sheets.googleapis.com/v4/spreadsheets"
TIMEOUT_SECONDS = 10
RETRYABLE_STATUSES = frozenset({408, 429, 500, 502, 503, 504})


class GoogleSheetsClient:
    def __init__(self, session: requests.Session, spreadsheet_id: str, title: str) -> None:
        self._session = session
        self._spreadsheet_id = spreadsheet_id
        self._title = title

    @classmethod
    def from_settings(cls) -> Self:
        # google-auth ships without type hints for these two calls.
        credentials = service_account.Credentials.from_service_account_file(  # type: ignore[no-untyped-call]
            str(settings.GOOGLE_SERVICE_ACCOUNT_FILE), scopes=[SCOPE]
        )
        return cls(
            AuthorizedSession(credentials),  # type: ignore[no-untyped-call]
            settings.GOOGLE_SPREADSHEET_ID,
            settings.GOOGLE_WORKSHEET_TITLE,
        )

    def exists(self, lead_id: str) -> bool:
        values = self._request("GET", self._url("A:A")).get("values", [])
        # Row 1 holds the headers (8.1).
        return any(row and row[0] == lead_id for row in values[1:])

    def append(self, row: SheetRow) -> None:
        # RAW keeps "=IMPORTXML(...)" from the form as plain text (formula injection, 13.1).
        self._request(
            "POST",
            self._url("A:H", ":append"),
            params={"valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS"},
            json={"values": [list(row)]},
        )

    def read_header(self) -> list[str]:
        values = self._request("GET", self._url("A1:H1")).get("values", [])
        return [str(cell) for cell in values[0]] if values else []

    def _url(self, a1: str, suffix: str = "") -> str:
        sheet = self._title.replace("'", "''")
        return f"{API}/{self._spreadsheet_id}/values/{quote(f"'{sheet}'!{a1}", safe='')}{suffix}"

    def _request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        try:
            response = self._session.request(method, url, timeout=TIMEOUT_SECONDS, **kwargs)
        except requests.Timeout as exc:
            raise SheetsRetryableError("timeout") from exc
        except (requests.ConnectionError, TransportError) as exc:
            raise SheetsRetryableError("connection") from exc
        except GoogleAuthError as exc:
            # A key that cannot mint tokens will not heal by retrying.
            raise SheetsPermanentError("auth") from exc
        status = response.status_code
        if status in RETRYABLE_STATUSES or status >= 500:
            raise SheetsRetryableError(status)
        if status >= 400:
            raise SheetsPermanentError(status)
        payload: dict[str, Any] = response.json() if response.content else {}
        return payload
