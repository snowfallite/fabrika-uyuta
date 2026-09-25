"""Google Sheets row contract (tech.md, 8.1): the app owns columns A..H, people own the rest."""

import re
import uuid
from collections.abc import Sequence
from datetime import tzinfo
from typing import Final

from apps.core.enums import ProductKind
from apps.leads.models import Lead

HEADERS: Final[tuple[str, ...]] = (
    "ID",
    "Дата",
    "ФИО",
    "Телефон",
    "Что заказать",
    "Размеры",
    "Комментарий",
    "Источник",
)
SheetRow = tuple[str, str, str, str, str, str, str, str]

COLUMNS: Final = "ABCDEFGH"
MAX_CELL: Final = 5000
DATE_RE: Final = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
E164_RE: Final = re.compile(r"^\+[1-9][0-9]{7,14}$")
PRODUCT_LABELS: Final = frozenset(label for _, label in ProductKind.choices)


class ContractViolation(Exception):
    """A row breaks 8.1. The message names the column and the rule, never the cell value."""


def build_row(lead: Lead, tz: tzinfo) -> SheetRow:
    return (
        str(lead.public_id),
        lead.created_at.astimezone(tz).strftime("%Y-%m-%d %H:%M"),
        lead.name,
        lead.phone,
        ProductKind(lead.product).label,
        lead.dimensions,
        lead.comment,
        lead.source_url,
    )


def validate_row(row: Sequence[object]) -> None:
    if len(row) != len(HEADERS):
        raise ContractViolation(f"row: expected {len(HEADERS)} cells, got {len(row)}")
    for column, cell in zip(COLUMNS, row, strict=True):
        if not isinstance(cell, str):
            raise ContractViolation(f"column {column}: must be a string")
        if len(cell) > MAX_CELL:
            raise ContractViolation(f"column {column}: longer than {MAX_CELL} characters")
    lead_id, created, _, phone, product = (str(cell) for cell in row[:5])
    if not _is_uuid4(lead_id):
        raise ContractViolation("column A: must be a lowercase UUID4")
    if not DATE_RE.match(created):
        raise ContractViolation("column B: must match YYYY-MM-DD HH:MM")
    if not E164_RE.match(phone):
        raise ContractViolation("column D: must be E.164")
    if product not in PRODUCT_LABELS:
        raise ContractViolation("column E: must be a ProductKind label")


def _is_uuid4(value: str) -> bool:
    try:
        parsed = uuid.UUID(value)
    except ValueError:
        return False
    return parsed.version == 4 and str(parsed) == value
