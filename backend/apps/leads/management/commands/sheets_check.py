from typing import Any

from django.core.management.base import BaseCommand, CommandError

from apps.leads.sheets.client import SheetsError, get_sheets_client
from apps.leads.sheets.row import HEADERS


class Command(BaseCommand):
    help = "Compare row 1 of the sheet with the 8.1 headers; exit 1 on mismatch or no access."

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            header = get_sheets_client().read_header()
        except SheetsError as exc:
            raise CommandError(
                f"Cannot read the sheet header: {exc.status} {type(exc).__name__}. Check that the "
                "service account is an editor and GOOGLE_WORKSHEET_TITLE names an existing sheet."
            ) from exc
        if tuple(header) != HEADERS:
            raise CommandError(
                f"Sheet header mismatch: expected {list(HEADERS)}, found {header}. "
                "Fix row 1 of the sheet (tech.md, 8.5)."
            )
        self.stdout.write("Sheet header matches tech.md 8.1.")
