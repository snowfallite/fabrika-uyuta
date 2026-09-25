from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def media_root(tmp_path: Path, settings: Any) -> Path:
    """Every content test writes images into its own empty media folder."""
    root = tmp_path / "media"
    root.mkdir()
    settings.MEDIA_ROOT = root
    return root
