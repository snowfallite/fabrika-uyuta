"""release: the one-off deploy step (tech.md, 16.3)."""

from typing import Any

import pytest
from django.core.management import call_command


@pytest.mark.parametrize(
    ("backend", "steps"),
    [
        ("fake", ["check", "migrate", "createcachetable", "sync_reference_data"]),
        ("google", ["check", "migrate", "createcachetable", "sync_reference_data", "sheets_check"]),
    ],
)
def test_release_runs_its_steps_in_order(
    monkeypatch: pytest.MonkeyPatch, settings: Any, backend: str, steps: list[str]
) -> None:
    settings.SHEETS_BACKEND = backend
    calls: list[str] = []
    monkeypatch.setattr(
        "apps.core.management.commands.release.call_command",
        lambda name, *args, **kwargs: calls.append(name),
    )
    call_command("release")
    assert calls == steps
