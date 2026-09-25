"""Sheet row contract (tech.md, 8.1)."""

import uuid
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest
from hypothesis import given
from hypothesis import strategies as st

from apps.core.enums import ProductKind
from apps.leads.models import Lead
from apps.leads.sheets.row import HEADERS, ContractViolation, build_row, validate_row

MOSCOW = ZoneInfo("Europe/Moscow")


def lead(**overrides: object) -> Lead:
    fields: dict[str, object] = {
        "public_id": uuid.uuid4(),
        "name": "Тестовый Клиент",
        "phone": "+79990000001",
        "product": ProductKind.WARDROBES,
        "dimensions": "",
        "comment": "",
        "source_url": "/",
        "created_at": datetime(2026, 9, 25, 21, 30, tzinfo=UTC),
    }
    return Lead(**(fields | overrides))


def test_headers_are_exact() -> None:
    assert HEADERS == (
        "ID",
        "Дата",
        "ФИО",
        "Телефон",
        "Что заказать",
        "Размеры",
        "Комментарий",
        "Источник",
    )


def test_build_row_formats_each_column() -> None:
    item = lead()
    row = build_row(item, MOSCOW)
    assert row == (
        str(item.public_id),
        "2026-09-26 00:30",
        "Тестовый Клиент",
        "+79990000001",
        "Шкафы",
        "",
        "",
        "/",
    )


@given(
    name=st.text(max_size=120),
    dimensions=st.text(max_size=300),
    comment=st.text(max_size=2000),
    source_url=st.text(max_size=500),
    product=st.sampled_from(ProductKind.values),
    phone=st.from_regex(r"\+[1-9][0-9]{7,14}", fullmatch=True),
    created_at=st.datetimes(
        min_value=datetime(2000, 1, 1), max_value=datetime(2100, 1, 1), timezones=st.just(UTC)
    ),
)
def test_build_row_always_fits_the_contract(
    name: str,
    dimensions: str,
    comment: str,
    source_url: str,
    product: str,
    phone: str,
    created_at: datetime,
) -> None:
    row = build_row(
        lead(
            name=name,
            dimensions=dimensions,
            comment=comment,
            source_url=source_url,
            product=product,
            phone=phone,
            created_at=created_at,
        ),
        MOSCOW,
    )
    assert len(row) == 8
    validate_row(row)
    assert row[4] == ProductKind(product).label


@pytest.mark.parametrize(
    ("index", "value", "column"),
    [
        (0, "not-a-uuid", "column A"),
        (0, str(uuid.uuid1()), "column A"),
        (1, "26.09.2026 00:30", "column B"),
        (3, "89990000001", "column D"),
        (4, "kitchens", "column E"),
        (6, "x" * 5001, "column G"),
    ],
)
def test_validate_row_names_the_column_not_the_value(index: int, value: str, column: str) -> None:
    row = list(build_row(lead(), MOSCOW))
    row[index] = value
    with pytest.raises(ContractViolation) as exc_info:
        validate_row(row)
    assert column in str(exc_info.value)
    assert value[:12] not in str(exc_info.value)


def test_validate_row_needs_eight_string_cells() -> None:
    with pytest.raises(ContractViolation, match="expected 8"):
        validate_row(("a",) * 7)
    with pytest.raises(ContractViolation, match="string"):
        validate_row((*build_row(lead(), MOSCOW)[:7], 5))
