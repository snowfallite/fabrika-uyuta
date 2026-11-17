"""In-memory or JSONL fake of the MAX chat. It validates every message, so a slice that sends
garbage fails loudly (tech.md, 25.2 and section 17)."""

import json
import threading
from pathlib import Path
from typing import Literal

from apps.leads.messenger.client import MessengerPermanentError, MessengerRetryableError
from apps.leads.messenger.text import validate_text

FailureKind = Literal["429", "500", "403", "success_false", "timeout"]


class FakeMessengerClient:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path
        self._memory: list[dict[str, object]] = []
        self._lock = threading.Lock()
        self._failures: list[FailureKind] = []
        self._lose_response = False

    def fail_next(self, kind: FailureKind, times: int = 1) -> None:
        self._failures.extend([kind] * times)

    def lose_response_once(self) -> None:
        """The next send stores the message, then reports a lost response."""
        self._lose_response = True

    def messages(self) -> list[dict[str, object]]:
        if self._path is None:
            return [dict(message) for message in self._memory]
        if not self._path.exists():
            return []
        with self._path.open(encoding="utf-8") as chat:
            return [json.loads(line) for line in chat if line.strip()]

    def send(self, chat_id: int, text: str) -> None:
        self._maybe_fail()
        validate_text(text)
        message: dict[str, object] = {"chat_id": chat_id, "text": text}
        with self._lock:
            if self._path is None:
                self._memory.append(message)
            else:
                self._path.parent.mkdir(parents=True, exist_ok=True)
                with self._path.open("a", encoding="utf-8") as chat:
                    chat.write(json.dumps(message, ensure_ascii=False) + "\n")
        if self._lose_response:
            self._lose_response = False
            raise MessengerRetryableError("timeout")

    def _maybe_fail(self) -> None:
        with self._lock:
            kind = self._failures.pop(0) if self._failures else None
        if kind == "403":
            raise MessengerPermanentError(403)
        if kind == "success_false":
            raise MessengerPermanentError("chat.denied")
        if kind == "timeout":
            raise MessengerRetryableError("timeout")
        if kind is not None:
            raise MessengerRetryableError(int(kind))
