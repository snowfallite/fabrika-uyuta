"""Sheets client seam (tech.md, 8.3): the worker talks to this interface only."""

from typing import Protocol

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from apps.leads.sheets.row import SheetRow


class SheetsClient(Protocol):
    def exists(self, lead_id: str) -> bool: ...
    def append(self, row: SheetRow) -> None: ...
    def read_header(self) -> list[str]: ...


class SheetsError(Exception):
    """Carries an HTTP status or a transport kind ("timeout", "connection"), never row data."""

    def __init__(self, status: int | str) -> None:
        super().__init__(str(status))
        self.status = status


class SheetsRetryableError(SheetsError): ...


class SheetsPermanentError(SheetsError): ...


def get_sheets_client() -> SheetsClient:
    if settings.SHEETS_BACKEND == "fake":
        from apps.leads.sheets.fake import FakeSheetsClient

        return FakeSheetsClient(settings.SHEETS_FAKE_PATH)
    if settings.SHEETS_BACKEND == "google":
        raise ImproperlyConfigured("SHEETS_BACKEND=google is not available yet (S2-04)")
    raise ImproperlyConfigured("SHEETS_BACKEND must be fake or google")
