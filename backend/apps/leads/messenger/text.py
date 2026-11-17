"""MAX message contract (tech.md, 25.3): plain text, one line per filled field."""

from datetime import tzinfo
from typing import Final

from apps.core.enums import ProductKind
from apps.core.phone import format_phone_display
from apps.leads.models import Lead

MAX_LENGTH: Final = 4000


class ContractViolation(Exception):
    """A message breaks 25.3. The message names the rule, never the lead text."""


def build_text(lead: Lead, tz: tzinfo) -> str:
    """The product goes in the first line, so it is not repeated as a row of its own."""
    label = ProductKind(lead.product).label
    rows = (
        ("Дата", lead.created_at.astimezone(tz).strftime("%Y-%m-%d %H:%M")),
        ("ФИО", lead.name),
        ("Телефон", format_phone_display(lead.phone)),
        ("Размеры", lead.dimensions),
        ("Комментарий", lead.comment),
        ("Источник", lead.source_url),
    )
    lines = [f"Новая заявка: {label}", ""]
    lines += [f"{name}: {value}" for name, value in rows if value]
    return "\n".join(lines)


def validate_text(text: str) -> None:
    if not text.strip():
        raise ContractViolation("text: must not be empty")
    if len(text) > MAX_LENGTH:
        raise ContractViolation(f"text: longer than {MAX_LENGTH} characters")
