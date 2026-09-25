"""Deploy checks: staging and production refuse dev values (tech.md, section 14)."""

from collections.abc import Sequence
from typing import Any

from django.apps import AppConfig
from django.conf import settings
from django.core.checks import CheckMessage, Error, register

DEV_SECRET_KEY = "dev-insecure-change-me"  # noqa: S105
DEV_INTERNAL_TOKEN = "dev-internal-token-change-me-0000000"  # noqa: S105


@register(deploy=True)
def check_production_settings(
    app_configs: Sequence[AppConfig] | None, **kwargs: Any
) -> list[CheckMessage]:
    if settings.APP_ENV not in {"staging", "production"}:
        return []
    problems = []
    if settings.DEBUG:
        problems.append(("DJANGO_DEBUG must be false", "core.E001"))
    if not settings.SECRET_KEY or settings.SECRET_KEY == DEV_SECRET_KEY:
        problems.append(("DJANGO_SECRET_KEY is empty or the dev value", "core.E002"))
    token = settings.INTERNAL_API_TOKEN
    if len(token) < 32 or token == DEV_INTERNAL_TOKEN:
        problems.append(("INTERNAL_API_TOKEN is shorter than 32 or the dev value", "core.E003"))
    if settings.DJANGO_ADMIN_PATH == "admin/":
        problems.append(("DJANGO_ADMIN_PATH must not be admin/", "core.E004"))
    if settings.ENABLE_TEST_ENDPOINTS:
        problems.append(("ENABLE_TEST_ENDPOINTS must be false", "core.E005"))
    if settings.SHEETS_BACKEND == "google" and not (
        settings.GOOGLE_SERVICE_ACCOUNT_FILE and settings.GOOGLE_SPREADSHEET_ID
    ):
        problems.append(("SHEETS_BACKEND=google needs GOOGLE_* variables", "core.E006"))
    return [Error(message, id=check_id) for message, check_id in problems]
