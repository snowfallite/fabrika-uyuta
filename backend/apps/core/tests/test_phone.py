"""S1-04 AC6 and properties of normalize_phone (tech.md, 12.3)."""

import json
import re
from pathlib import Path
from typing import Any

import pytest
from django.conf import settings
from hypothesis import given
from hypothesis import strategies as st

from apps.core.phone import format_phone_display, normalize_phone

CASES: list[dict[str, Any]] = json.loads(
    (Path(settings.BASE_DIR).parent / "contracts/fixtures/phone-cases.json").read_text("utf-8")
)
E164 = re.compile(r"^\+[1-9][0-9]{7,14}$")
RU_MOBILE = st.from_regex(r"9[0-9]{9}", fullmatch=True)
SEPARATORS = st.sampled_from([" ", "-", "(", ")", "  ", ""])


@pytest.mark.parametrize("case", CASES, ids=[c["input"] or "<empty>" for c in CASES])
def test_ac6_normalize_phone_matches_fixture(case: dict[str, Any]) -> None:
    assert normalize_phone(case["input"]) == case["e164"]
    assert normalize_phone(case["masked"]) == case["e164"]


@pytest.mark.parametrize("case", [c for c in CASES if c["e164"] and c["e164"].startswith("+7")])
def test_ac6_format_phone_display_matches_mask(case: dict[str, Any]) -> None:
    assert format_phone_display(case["e164"]) == case["masked"]


@given(st.text())
def test_normalize_never_raises_and_returns_e164_or_none(raw: str) -> None:
    result = normalize_phone(raw)
    assert result is None or E164.fullmatch(result)


@given(st.text(alphabet="+0123456789 ()-", max_size=20))
def test_normalize_is_idempotent_on_its_output(raw: str) -> None:
    result = normalize_phone(raw)
    if result is not None:
        assert normalize_phone(result) == result


@given(RU_MOBILE, st.lists(SEPARATORS, min_size=10, max_size=10))
def test_separators_do_not_matter(digits: str, separators: list[str]) -> None:
    spaced = "".join(d + s for d, s in zip(digits, separators, strict=True))
    assert normalize_phone("+7" + spaced) == normalize_phone("+7" + digits)


@given(RU_MOBILE)
def test_eight_and_plus_seven_give_the_same_number(digits: str) -> None:
    assert normalize_phone("8" + digits) == normalize_phone("+7" + digits)
