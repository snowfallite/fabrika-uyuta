"""Print the chat ids MAX reports so the owner can fill the admin field (tech.md, 25.1)."""

from typing import Any

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser

from apps.leads.messenger.max import build_session

CHAT_EVENTS = ["bot_added", "bot_started", "message_created", "user_added"]
DEFAULT_WAIT = 30


def chat_ids(updates: list[dict[str, Any]]) -> dict[int, str]:
    """chat_id sits at the top level of most events and inside message.recipient for the rest."""
    chats: dict[int, str] = {}
    for update in updates:
        recipient = (update.get("message") or {}).get("recipient") or {}
        raw = update.get("chat_id")
        if raw is None:
            raw = recipient.get("chat_id")
        if raw is not None:
            chats.setdefault(int(raw), str(update.get("update_type", "")))
    return chats


class Command(BaseCommand):
    help = "Print MAX chat ids from recent bot events; the owner copies one into the admin."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--wait", type=int, default=DEFAULT_WAIT, help="Long polling timeout, seconds."
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if not settings.MAX_BOT_TOKEN:
            raise CommandError("MAX_BOT_TOKEN is empty: create the bot first (tech.md, 25.1).")
        wait = int(options["wait"])
        session = build_session(settings.MAX_BOT_TOKEN, settings.MAX_CA_BUNDLE)
        params: dict[str, int | list[str]] = {"timeout": wait, "types": CHAT_EVENTS}
        try:
            response = session.get(
                f"{settings.MAX_API_URL}/updates", params=params, timeout=wait + 5
            )
        except requests.RequestException as exc:
            raise CommandError(f"MAX is unreachable: {type(exc).__name__}.") from exc
        if response.status_code != 200:
            raise CommandError(
                f"MAX answered {response.status_code}. Check MAX_BOT_TOKEN and MAX_CA_BUNDLE."
            )
        chats = chat_ids(response.json().get("updates", []))
        if not chats:
            self.stdout.write(
                "Событий нет. Добавьте бота в чат или напишите в чат, затем повторите команду."
            )
            return
        for chat_id, event in sorted(chats.items()):
            self.stdout.write(f"chat_id={chat_id}  событие={event}")
        self.stdout.write(
            "Впишите нужный chat_id в админке: Контакты, поле «Чат в MAX для заявок»."
        )
