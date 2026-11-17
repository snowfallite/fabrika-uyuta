"""Messenger client seam (tech.md, 25.2): the outbox talks to this interface only."""

from typing import Protocol

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class MessengerClient(Protocol):
    def send(self, chat_id: int, text: str) -> None: ...


class MessengerError(Exception):
    """Carries an HTTP status, a MAX error code or a transport kind, never the message text."""

    def __init__(self, status: int | str) -> None:
        super().__init__(str(status))
        self.status = status


class MessengerRetryableError(MessengerError): ...


class MessengerPermanentError(MessengerError): ...


def get_messenger_client() -> MessengerClient:
    if settings.MAX_BACKEND == "fake":
        from apps.leads.messenger.fake import FakeMessengerClient

        return FakeMessengerClient(settings.MAX_FAKE_PATH)
    if settings.MAX_BACKEND == "max":
        from apps.leads.messenger.max import MaxMessengerClient

        return MaxMessengerClient.from_settings()
    raise ImproperlyConfigured("MAX_BACKEND must be fake or max")
