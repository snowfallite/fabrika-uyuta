"""S2-17 AC5 and AC6: the kind label of a lead, snapshot first (tech.md, section 6)."""

import uuid
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from hypothesis import given
from hypothesis import strategies as st

from apps.core.enums import ProductKind
from apps.leads.messenger.text import build_text
from apps.leads.models import Lead
from apps.leads.notify import build_message
from apps.leads.product import product_label
from apps.leads.sheets.row import build_row

MOSCOW = ZoneInfo("Europe/Moscow")
CARD = "https://example.com/secret-admin/leads/lead/1/change/"


def lead(product: str, snapshot: str) -> Lead:
    """Fictitious data only (tech.md, 13.1); nothing here touches the database."""
    return Lead(
        public_id=uuid.uuid4(),
        name="Тестовый Клиент",
        phone="+79990000001",
        product=product,
        product_label=snapshot,
        dimensions="",
        comment="",
        source_url="/",
        created_at=datetime(2026, 11, 19, 11, 20, tzinfo=UTC),
    )


def test_ac6_the_snapshot_wins_over_the_current_category() -> None:
    assert product_label(lead("kitchens", "Кухни под заказ, лето 2026")) == (
        "Кухни под заказ, лето 2026"
    )


def test_ac6_a_lead_from_before_v15_falls_back_to_the_enum_label() -> None:
    assert product_label(lead("kitchens", "")) == "Кухни под заказ"


def test_ac6_an_unknown_slug_goes_out_as_it_is() -> None:
    assert product_label(lead("loft-beds", "")) == "loft-beds"


@given(product=st.text(max_size=32), snapshot=st.text(max_size=120))
def test_the_label_is_the_snapshot_or_a_fallback_and_never_raises(
    product: str, snapshot: str
) -> None:
    label = product_label(lead(product, snapshot))

    if snapshot:
        assert label == snapshot
    elif product in ProductKind.values:
        assert label == ProductKind(product).label
    else:
        assert label == product


def test_ac5_the_sheet_the_email_and_the_chat_take_the_snapshot() -> None:
    own = lead("kids-rooms", "Детские комнаты")

    assert build_row(own, MOSCOW)[4] == "Детские комнаты"
    message = build_message(own, MOSCOW, CARD)
    assert message.subject == "Фабрика Уюта: новая заявка, Детские комнаты"
    assert "Что заказать: Детские комнаты" in message.body
    assert build_text(own, MOSCOW).startswith("<b>Новая заявка: Детские комнаты</b>")


def test_ac6_a_lead_from_before_v15_reads_the_same_everywhere() -> None:
    old = lead("office", "")

    assert build_row(old, MOSCOW)[4] == "Офисная мебель"
    assert build_message(old, MOSCOW, CARD).subject.endswith("Офисная мебель")
    assert build_text(old, MOSCOW).startswith("<b>Новая заявка: Офисная мебель</b>")
