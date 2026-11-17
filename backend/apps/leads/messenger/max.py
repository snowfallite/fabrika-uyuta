"""MAX Bot API transport (tech.md, 25.2): plain requests, no SDK, text without markup."""

from typing import Any, Self

import requests
from django.conf import settings

from apps.leads.messenger.client import MessengerPermanentError, MessengerRetryableError

TIMEOUT_SECONDS = 10
RETRYABLE_STATUSES = frozenset({408, 429, 500, 502, 503, 504})


def build_session(token: str, ca_bundle: str) -> requests.Session:
    """MAX takes the token bare, and certifi rejects the chain platform-api2.max.ru serves."""
    session = requests.Session()
    session.headers["Authorization"] = token
    session.verify = ca_bundle or True
    return session


class MaxMessengerClient:
    def __init__(self, session: requests.Session, api_url: str) -> None:
        self._session = session
        self._api_url = api_url

    @classmethod
    def from_settings(cls) -> Self:
        return cls(
            build_session(settings.MAX_BOT_TOKEN, settings.MAX_CA_BUNDLE), settings.MAX_API_URL
        )

    def send(
        self, chat_id: int, text: str, attachments: list[dict[str, object]] | None = None
    ) -> None:
        # The template owns the markup; every lead value is escaped before it gets here (13.1).
        body: dict[str, Any] = {"text": text, "format": "html"}
        if attachments:
            body["attachments"] = attachments
        self._request("POST", "/messages", params={"chat_id": chat_id}, json=body)

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        try:
            response = self._session.request(
                method, f"{self._api_url}{path}", timeout=TIMEOUT_SECONDS, **kwargs
            )
        except requests.Timeout as exc:
            raise MessengerRetryableError("timeout") from exc
        except requests.ConnectionError as exc:
            raise MessengerRetryableError("connection") from exc
        status = response.status_code
        if status in RETRYABLE_STATUSES or status >= 500:
            raise MessengerRetryableError(status)
        if status >= 400:
            raise MessengerPermanentError(status)
        payload: dict[str, Any] = response.json() if response.content else {}
        # MAX answers 200 with success=false for a wrong chat, a bot outside it or a bad token.
        if payload.get("success") is False:
            raise MessengerPermanentError(str(payload.get("code") or "success.false"))
        return payload
