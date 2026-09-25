"""Environment readers. Only config/settings.py calls them (tech.md, section 14)."""

import os

from django.core.exceptions import ImproperlyConfigured

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off", ""}


def env_str(name: str, default: str | None = None) -> str:
    value = os.environ.get(name)
    if value is None:
        if default is None:
            raise ImproperlyConfigured(f"Environment variable {name} is not set")
        return default
    return value.strip()


def env_bool(name: str, default: bool | None = None) -> bool:
    raw = env_str(name, None if default is None else str(default).lower()).lower()
    if raw in _TRUE:
        return True
    if raw in _FALSE:
        return False
    raise ImproperlyConfigured(f"Environment variable {name} must be true or false")


def env_int(name: str, default: int | None = None) -> int:
    raw = env_str(name, None if default is None else str(default))
    try:
        return int(raw)
    except ValueError as exc:
        raise ImproperlyConfigured(f"Environment variable {name} must be an integer") from exc


def env_list(name: str, default: str | None = None) -> list[str]:
    return [item.strip() for item in env_str(name, default).split(",") if item.strip()]
