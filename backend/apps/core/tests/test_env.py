import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from apps.core.env import env_bool, env_int, env_list, env_str


def test_env_str_requires_value_without_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FABRIKA_TEST_VAR", raising=False)
    with pytest.raises(ImproperlyConfigured):
        env_str("FABRIKA_TEST_VAR")
    assert env_str("FABRIKA_TEST_VAR", "fallback") == "fallback"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("true", True), ("True", True), ("1", True), ("false", False), ("", False)],
)
def test_env_bool_parses_flags(monkeypatch: pytest.MonkeyPatch, raw: str, expected: bool) -> None:
    monkeypatch.setenv("FABRIKA_TEST_VAR", raw)
    assert env_bool("FABRIKA_TEST_VAR") is expected


def test_env_bool_and_int_reject_garbage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FABRIKA_TEST_VAR", "maybe")
    with pytest.raises(ImproperlyConfigured):
        env_bool("FABRIKA_TEST_VAR")
    with pytest.raises(ImproperlyConfigured):
        env_int("FABRIKA_TEST_VAR")


def test_env_list_splits_and_drops_blanks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FABRIKA_TEST_VAR", "localhost, 127.0.0.1,,backend ")
    assert env_list("FABRIKA_TEST_VAR") == ["localhost", "127.0.0.1", "backend"]


def test_settings_follow_section_14() -> None:
    assert settings.LANGUAGE_CODE == "ru"
    assert settings.TIME_ZONE == "Europe/Moscow"
    assert settings.USE_TZ is True
    assert settings.STATIC_URL == "/django-static/"
    assert settings.MEDIA_URL == "/media/"
    assert settings.CACHES["default"] == {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
        "OPTIONS": {"MAX_ENTRIES": 10000},
    }
