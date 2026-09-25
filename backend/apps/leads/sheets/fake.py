"""In-memory or JSONL fake of the sheet. It validates every row, so a slice that sends garbage
fails loudly (tech.md, 8.3 and section 17)."""

import json
import threading
from pathlib import Path
from typing import Literal

from apps.leads.sheets.client import SheetsPermanentError, SheetsRetryableError
from apps.leads.sheets.row import HEADERS, SheetRow, validate_row

FailureKind = Literal["429", "500", "403", "timeout"]


class FakeSheetsClient:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path
        self._memory: list[list[str]] = []
        self._lock = threading.Lock()
        self._failures: list[FailureKind] = []
        self._lose_response = False

    def fail_next(self, kind: FailureKind, times: int = 1) -> None:
        self._failures.extend([kind] * times)

    def lose_response_once(self) -> None:
        """The next append writes the row, then reports a lost response."""
        self._lose_response = True

    def rows(self) -> list[list[str]]:
        if self._path is None:
            return [list(row) for row in self._memory]
        if not self._path.exists():
            return []
        with self._path.open(encoding="utf-8") as sheet:
            return [json.loads(line) for line in sheet if line.strip()]

    def exists(self, lead_id: str) -> bool:
        self._maybe_fail()
        return any(row[0] == lead_id for row in self.rows())

    def append(self, row: SheetRow) -> None:
        self._maybe_fail()
        validate_row(row)
        with self._lock:
            if self._path is None:
                self._memory.append(list(row))
            else:
                self._path.parent.mkdir(parents=True, exist_ok=True)
                with self._path.open("a", encoding="utf-8") as sheet:
                    sheet.write(json.dumps(list(row), ensure_ascii=False) + "\n")
        if self._lose_response:
            self._lose_response = False
            raise SheetsRetryableError("timeout")

    def read_header(self) -> list[str]:
        return list(HEADERS)

    def _maybe_fail(self) -> None:
        with self._lock:
            kind = self._failures.pop(0) if self._failures else None
        if kind == "403":
            raise SheetsPermanentError(403)
        if kind == "timeout":
            raise SheetsRetryableError("timeout")
        if kind is not None:
            raise SheetsRetryableError(int(kind))
