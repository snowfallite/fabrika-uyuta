"""Client IP resolution: one trusted proxy (Caddy) and the SvelteKit BFF."""

import ipaddress
from collections.abc import Mapping
from typing import Any

from django.http import HttpRequest


def _valid_ip(value: str) -> str | None:
    try:
        return str(ipaddress.ip_address(value.strip()))
    except ValueError:
        return None


def forwarded_client_ip(request: HttpRequest) -> str | None:
    """Admin requests: Caddy is the only proxy and appends the peer address last."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = _valid_ip(forwarded.split(",")[-1]) if forwarded else None
    return ip or request.META.get("REMOTE_ADDR")


def api_client_ip(meta: Mapping[str, Any]) -> str | None:
    """API requests: SvelteKit passes the visitor IP in X-Client-IP (tech.md, section 7)."""
    return _valid_ip(str(meta.get("HTTP_X_CLIENT_IP", ""))) or meta.get("REMOTE_ADDR")
