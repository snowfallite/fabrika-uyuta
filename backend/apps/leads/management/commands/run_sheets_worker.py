import random
from typing import Any

from django.core.management.base import BaseCommand

from apps.leads.sheets.client import get_sheets_client
from apps.leads.worker import run_forever


class Command(BaseCommand):
    help = "Deliver pending leads to Google Sheets until SIGTERM (tech.md, 8.4)."

    def handle(self, *args: Any, **options: Any) -> None:
        run_forever(get_sheets_client(), random.Random())  # noqa: S311  jitter, not crypto
