"""S1-04 AC5: check --deploy fails in production on every unsafe setting."""

from pathlib import Path
from typing import Any

import pytest
from django.core.management import call_command
from django.core.management.base import SystemCheckError
from django.test import override_settings

SAFE_PRODUCTION: dict[str, Any] = {
    "APP_ENV": "production",
    "DEBUG": False,
    "SECRET_KEY": "x" * 60,
    "INTERNAL_API_TOKEN": "t" * 40,
    "DJANGO_ADMIN_PATH": "secret-admin/",
    "ENABLE_TEST_ENDPOINTS": False,
    "SHEETS_BACKEND": "google",
    "GOOGLE_SERVICE_ACCOUNT_FILE": Path("/run/secrets/google-sa.json"),
    "GOOGLE_SPREADSHEET_ID": "sheet-id",
}

UNSAFE = [
    ("DEBUG", True),
    ("SECRET_KEY", "dev-insecure-change-me"),
    ("INTERNAL_API_TOKEN", "short-token"),
    ("INTERNAL_API_TOKEN", "dev-internal-token-change-me-0000000"),
    ("DJANGO_ADMIN_PATH", "admin/"),
    ("ENABLE_TEST_ENDPOINTS", True),
    ("GOOGLE_SERVICE_ACCOUNT_FILE", None),
    ("GOOGLE_SPREADSHEET_ID", ""),
]


def deploy_check() -> None:
    call_command("check", deploy=True, stdout=None, stderr=None)


def test_ac5_safe_production_passes() -> None:
    with override_settings(**SAFE_PRODUCTION):
        deploy_check()


@pytest.mark.parametrize(("name", "value"), UNSAFE)
def test_ac5_each_unsafe_setting_fails(name: str, value: Any) -> None:
    with override_settings(**(SAFE_PRODUCTION | {name: value})), pytest.raises(SystemCheckError):
        deploy_check()


def test_ac5_dev_values_are_fine_outside_staging_and_production() -> None:
    with override_settings(**(SAFE_PRODUCTION | {"APP_ENV": "dev", "DEBUG": True})):
        deploy_check()
