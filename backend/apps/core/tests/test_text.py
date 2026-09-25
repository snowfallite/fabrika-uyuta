"""clean_name and clean_text (tech.md, 12.1)."""

import unicodedata

from hypothesis import given
from hypothesis import strategies as st

from apps.core.text import clean_name, clean_text


def controls(value: str, allowed: str = "") -> list[str]:
    return [ch for ch in value if unicodedata.category(ch) in {"Cc", "Cs"} and ch not in allowed]


@given(st.text())
def test_clean_name_is_idempotent_and_tidy(raw: str) -> None:
    once = clean_name(raw)
    assert clean_name(once) == once
    assert controls(once) == []
    assert once == once.strip()
    assert "  " not in once
    assert len(once) <= len(raw)


@given(st.text())
def test_clean_text_is_idempotent_and_tidy(raw: str) -> None:
    once = clean_text(raw)
    assert clean_text(once) == once
    assert controls(once, allowed="\n\t") == []
    assert once == once.strip()
    assert len(once) <= len(raw)


def test_examples() -> None:
    assert clean_name("  Анна  Мария\n Иванова ") == "Анна Мария Иванова"
    assert clean_text(" a\x00b\r\n\tc ") == "ab\n\tc"
