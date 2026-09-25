from typing import Any

import pytest
from hypothesis import settings as hypothesis_settings

hypothesis_settings.register_profile("ci", max_examples=200, deadline=None, derandomize=True)
hypothesis_settings.register_profile("dev", max_examples=50, deadline=None)
hypothesis_settings.load_profile("dev")


@pytest.fixture(autouse=True)
def _plain_static_storage(settings: Any) -> None:
    """Admin pages render without a collectstatic manifest in tests."""
    settings.STORAGES = settings.STORAGES | {
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}
    }
