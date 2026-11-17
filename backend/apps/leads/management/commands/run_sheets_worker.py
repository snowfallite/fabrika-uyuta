import random
from typing import Any

from django.core.management.base import BaseCommand

from apps.leads.messenger.client import get_messenger_client
from apps.leads.sheets.client import get_sheets_client
from apps.leads.worker import run_forever


class Command(BaseCommand):
    help = "Deliver pending leads to the sheet, the managers and the chat (tech.md, 8.4, 24, 25)."

    def handle(self, *args: Any, **options: Any) -> None:
        run_forever(
            get_sheets_client(),
            get_messenger_client(),
            random.Random(),  # noqa: S311  jitter, not crypto
        )
