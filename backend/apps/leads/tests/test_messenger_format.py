"""S2-15: HTML formatting and the copy-phone button (tech.md, 25.3)."""

import random
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from django.utils import timezone
from hypothesis import given
from hypothesis import strategies as st

from apps.content.models import SiteSettings
from apps.core.enums import NotifyStatus, ProductKind
from apps.leads.messenger.fake import FakeMessengerClient
from apps.leads.messenger.outbox import send_lead
from apps.leads.messenger.text import COPY_BUTTON, ELLIPSIS, MAX_LENGTH, build_text, validate_text
from apps.leads.models import Lead
from apps.leads.tests.factories import make_lead

pytestmark = pytest.mark.django_db
RNG = random.Random(0)  # noqa: S311  jitter only
CHAT_ID = -12307927
TZ = ZoneInfo("Europe/Moscow")


@pytest.fixture(autouse=True)
def chat_on(settings: Any) -> None:
    settings.SHEETS_TIMEZONE = "Europe/Moscow"
    SiteSettings.objects.update_or_create(id=1, defaults={"max_chat_id": CHAT_ID})


def sent(**overrides: Any) -> dict[str, object]:
    """One lead through the outbox; returns the message the fake chat recorded."""
    lead = make_lead(**({"max_status": NotifyStatus.PENDING} | overrides))
    chat = FakeMessengerClient()
    send_lead(lead.pk, chat, timezone.now(), RNG)
    return chat.messages()[0]


def test_ac1_labels_are_bold_and_values_are_not() -> None:
    text = str(sent(comment="обычный текст")["text"])

    assert text.startswith("<b>Новая заявка: Кухни под заказ</b>")
    assert "<b>Комментарий:</b> обычный текст" in text
    for label in ("Дата", "ФИО", "Телефон", "Комментарий"):
        assert f"<b>{label}:</b> " in text


def test_ac2_markup_from_the_comment_arrives_as_text() -> None:
    text = str(sent(name="Иван <script>", comment="<b>злой</b> [ссылка](http://зло)")["text"])

    assert "<b>Комментарий:</b> &lt;b&gt;злой&lt;/b&gt; [ссылка](http://зло)" in text
    assert "<b>злой</b>" not in text
    assert "<script>" not in text
    assert "&lt;script&gt;" in text


def test_ac3_an_escape_heavy_comment_is_trimmed_to_the_limit() -> None:
    text = str(sent(comment="&" * 2000)["text"])

    validate_text(text)
    assert len(text) <= MAX_LENGTH
    assert ELLIPSIS in text
    assert "&amp;" in text


def test_ac3_the_message_fits_when_every_field_is_an_escape_bomb() -> None:
    text = str(
        sent(name="&" * 120, dimensions="&" * 300, comment="&" * 2000, source_url="&" * 500)["text"]
    )

    validate_text(text)
    assert len(text) <= MAX_LENGTH


def test_ac4_the_message_carries_one_copy_phone_button() -> None:
    message = sent(phone="+79991234567")

    assert COPY_BUTTON == "Скопировать телефон"
    assert message["attachments"] == [
        {
            "type": "inline_keyboard",
            "payload": {
                "buttons": [[{"type": "clipboard", "text": COPY_BUTTON, "payload": "+79991234567"}]]
            },
        }
    ]


def test_ac5_empty_fields_drop_their_rows_and_keep_the_button() -> None:
    message = sent(dimensions="", comment="", source_url="")

    text = str(message["text"])
    for label in ("Размеры", "Комментарий", "Источник"):
        assert label not in text
    assert message["attachments"]


@given(
    name=st.text(min_size=1, max_size=120),
    dimensions=st.text(max_size=300),
    comment=st.text(max_size=2000),
    source=st.text(max_size=500),
)
def test_build_text_never_outgrows_the_limit_and_leaks_no_markup(
    name: str, dimensions: str, comment: str, source: str
) -> None:
    lead = Lead(
        name=name,
        phone="+79991234567",
        product=ProductKind.KITCHENS,
        dimensions=dimensions,
        comment=comment,
        source_url=source,
        created_at=timezone.now(),
    )

    text = build_text(lead, TZ)

    validate_text(text)
    assert len(text) <= MAX_LENGTH
    # Strip the template's own tags: nothing that could open a tag may be left.
    assert "<" not in text.replace("<b>", "").replace("</b>", "")
