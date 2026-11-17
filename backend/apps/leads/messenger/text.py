"""MAX message contract (tech.md, 25.3): HTML labels, escaped values, one clipboard button."""

import html
from collections.abc import Sequence
from datetime import tzinfo
from typing import Final

from apps.core.enums import ProductKind
from apps.core.phone import format_phone_display
from apps.leads.models import Lead

MAX_LENGTH: Final = 4000
COPY_BUTTON: Final = "Скопировать телефон"
ELLIPSIS: Final = "…"


class ContractViolation(Exception):
    """A message breaks 25.3. The message names the rule, never the lead text."""


def build_text(lead: Lead, tz: tzinfo) -> str:
    """Labels in <b>, values escaped. Values are trimmed in order, so the whole fits MAX_LENGTH."""
    label = ProductKind(lead.product).label
    head = f"<b>Новая заявка: {html.escape(label)}</b>"
    lines = [head, ""]
    budget = MAX_LENGTH - len(head) - 1
    for name, value in _rows(lead, tz):
        if not value:
            continue
        prefix = f"<b>{name}:</b> "
        # The newline that will join this row counts against the limit too.
        room = budget - len(prefix) - 1
        if room <= 0:
            break
        line = prefix + _fit(value, room)
        lines.append(line)
        budget -= len(line) + 1
    return "\n".join(lines)


def build_keyboard(lead: Lead) -> list[dict[str, object]]:
    """One clipboard button: it copies the phone on the client, with no handler of ours (25.3)."""
    return [
        {
            "type": "inline_keyboard",
            "payload": {
                "buttons": [[{"type": "clipboard", "text": COPY_BUTTON, "payload": lead.phone}]]
            },
        }
    ]


def validate_text(text: str) -> None:
    if not text.strip():
        raise ContractViolation("text: must not be empty")
    if len(text) > MAX_LENGTH:
        raise ContractViolation(f"text: longer than {MAX_LENGTH} characters")


def _rows(lead: Lead, tz: tzinfo) -> Sequence[tuple[str, str]]:
    """The product goes in the first line, so it is not repeated as a row of its own."""
    return (
        ("Дата", lead.created_at.astimezone(tz).strftime("%Y-%m-%d %H:%M")),
        ("ФИО", lead.name),
        ("Телефон", format_phone_display(lead.phone)),
        ("Размеры", lead.dimensions),
        ("Комментарий", lead.comment),
        ("Источник", lead.source_url),
    )


def _fit(value: str, room: int) -> str:
    """Escape the value; if it outgrows the room, keep whole characters and mark the cut.

    Escaping stretches the text, one "&" costs five characters, so a long comment or a query
    string full of ampersands has to pay for itself instead of breaking the 4000 limit.
    """
    escaped = html.escape(value)
    if len(escaped) <= room:
        return escaped
    kept: list[str] = []
    used = len(ELLIPSIS)
    for char in value:
        cost = len(html.escape(char))
        if used + cost > room:
            break
        kept.append(char)
        used += cost
    # html.escape replaces single characters, so escaping the kept prefix costs exactly `used`.
    return html.escape("".join(kept)) + ELLIPSIS
