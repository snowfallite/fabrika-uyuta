"""S2-14: MAX Bot API transport and chat binding (tech.md, 25.1, 25.2)."""

import json
from io import StringIO
from typing import Any

import pytest
import requests
import responses
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.content.models import SiteSettings
from apps.leads.messenger.client import MessengerPermanentError, MessengerRetryableError
from apps.leads.messenger.max import MaxMessengerClient, build_session

API = "https://max.test"
TOKEN = "bot-token-123"  # noqa: S105  fictitious
BUNDLE = "/etc/ssl/certs/russian-trusted-root-ca.pem"
RETRYABLE = [408, 429, 500, 502, 503, 504]
PERMANENT = [400, 401, 403, 404, 405]


def client() -> MaxMessengerClient:
    return MaxMessengerClient(build_session(TOKEN, ""), API)


@responses.activate
def test_ac9_send_posts_the_text_to_the_chat() -> None:
    responses.post(f"{API}/messages", json={"message": {"body": {"mid": "m1"}}}, status=200)

    client().send(-12307927, "Новая заявка: =1+1")

    request = responses.calls[0].request
    assert request.headers["Authorization"] == TOKEN
    assert "chat_id=-12307927" in str(request.url)
    body = request.body
    assert isinstance(body, bytes | str)
    # S2-15 AC1: html markup comes from the template, lead values arrive escaped (tech.md, 13.1).
    assert json.loads(body) == {"text": "Новая заявка: =1+1", "format": "html"}


@responses.activate
def test_ac4_send_passes_the_keyboard_through() -> None:
    responses.post(f"{API}/messages", json={}, status=200)
    keyboard: list[dict[str, object]] = [
        {"type": "inline_keyboard", "payload": {"buttons": [[{"type": "clipboard"}]]}}
    ]

    client().send(-1, "текст", keyboard)

    body = responses.calls[0].request.body
    assert isinstance(body, bytes | str)
    assert json.loads(body)["attachments"] == keyboard


def test_ac9_the_session_verifies_against_the_given_bundle() -> None:
    assert build_session(TOKEN, BUNDLE).verify == BUNDLE
    # Empty bundle keeps the default store: dev and e2e run against the fake anyway.
    assert build_session(TOKEN, "").verify is True


@pytest.mark.parametrize("status", RETRYABLE)
@responses.activate
def test_ac3_server_side_statuses_are_retryable(status: int) -> None:
    responses.post(f"{API}/messages", json={}, status=status)

    with pytest.raises(MessengerRetryableError) as caught:
        client().send(-1, "текст")

    assert caught.value.status == status


@pytest.mark.parametrize("status", PERMANENT)
@responses.activate
def test_ac4_client_side_statuses_are_permanent(status: int) -> None:
    responses.post(f"{API}/messages", json={}, status=status)

    with pytest.raises(MessengerPermanentError) as caught:
        client().send(-1, "текст")

    assert caught.value.status == status


@responses.activate
def test_ac4_success_false_is_permanent() -> None:
    responses.post(f"{API}/messages", json={"success": False, "code": "chat.denied"}, status=200)

    with pytest.raises(MessengerPermanentError) as caught:
        client().send(-1, "текст")

    assert caught.value.status == "chat.denied"


@pytest.mark.parametrize(
    ("error", "kind"),
    [(requests.Timeout(), "timeout"), (requests.ConnectionError(), "connection")],
)
@responses.activate
def test_ac3_transport_failures_are_retryable(error: Exception, kind: str) -> None:
    responses.post(f"{API}/messages", body=error)

    with pytest.raises(MessengerRetryableError) as caught:
        client().send(-1, "текст")

    assert caught.value.status == kind


@pytest.fixture
def bot(settings: Any) -> None:
    settings.MAX_API_URL = API
    settings.MAX_BOT_TOKEN = TOKEN
    settings.MAX_CA_BUNDLE = ""


@responses.activate
def test_ac11_bind_prints_a_chat_id_per_event(bot: None) -> None:
    responses.get(
        f"{API}/updates",
        json={
            "updates": [
                {"update_type": "bot_added", "chat_id": -12307927},
                {"update_type": "message_created", "message": {"recipient": {"chat_id": -55}}},
                {"update_type": "bot_added", "chat_id": -12307927},
            ]
        },
        status=200,
    )
    out = StringIO()

    call_command("max_bind_chat", "--wait", "0", stdout=out)

    printed = out.getvalue()
    assert "chat_id=-12307927" in printed
    assert "chat_id=-55" in printed
    assert printed.count("chat_id=") == 2


@responses.activate
def test_ac11_bind_says_so_when_no_event_arrived(bot: None) -> None:
    responses.get(f"{API}/updates", json={"updates": []}, status=200)
    out = StringIO()

    call_command("max_bind_chat", "--wait", "0", stdout=out)

    assert "Событий нет" in out.getvalue()


@pytest.mark.django_db
@responses.activate
def test_ac11_bind_writes_nothing_to_the_database(bot: None) -> None:
    SiteSettings.objects.create(id=1)
    responses.get(
        f"{API}/updates",
        json={"updates": [{"update_type": "bot_added", "chat_id": -42}]},
        status=200,
    )

    call_command("max_bind_chat", "--wait", "0", stdout=StringIO())

    assert SiteSettings.objects.get(id=1).max_chat_id is None


def test_ac11_bind_refuses_an_empty_token(settings: Any) -> None:
    settings.MAX_BOT_TOKEN = ""

    with pytest.raises(CommandError, match="MAX_BOT_TOKEN"):
        call_command("max_bind_chat", stdout=StringIO())


@responses.activate
def test_ac11_bind_reports_a_refused_token(bot: None) -> None:
    responses.get(f"{API}/updates", json={}, status=401)

    with pytest.raises(CommandError, match="401"):
        call_command("max_bind_chat", "--wait", "0", stdout=StringIO())
