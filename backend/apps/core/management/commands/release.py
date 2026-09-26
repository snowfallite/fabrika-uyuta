from typing import Any

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "One-off deploy step: deploy checks, migrations, cache table, reference data, sheet."

    def handle(self, *args: Any, **options: Any) -> None:
        call_command("check", deploy=True)
        call_command("migrate", interactive=False)
        call_command("createcachetable")
        call_command("sync_reference_data")
        if settings.SHEETS_BACKEND == "google":
            call_command("sheets_check")
