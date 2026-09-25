from typing import Any

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.content.models import Category, SiteImage, SiteSettings
from apps.core.enums import CATEGORY_SLUG_CHOICES, SiteImageSlot

CONTENT_GROUP = "Контент"
LEADS_GROUP = "Заявки"


class Command(BaseCommand):
    help = "Create missing reference rows and admin groups; never overwrite existing values."

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        for position, (slug, label) in enumerate(CATEGORY_SLUG_CHOICES):
            Category.objects.get_or_create(
                slug=slug, defaults={"title": label, "position": position}
            )
        for slot in SiteImageSlot.values:
            SiteImage.objects.get_or_create(slot=slot)
        SiteSettings.objects.get_or_create(id=1)

        # Permissions go in only on creation, so the owner's later edits stay.
        group, created = Group.objects.get_or_create(name=CONTENT_GROUP)
        if created:
            group.permissions.set(Permission.objects.filter(content_type__app_label="content"))
        group, created = Group.objects.get_or_create(name=LEADS_GROUP)
        if created:
            group.permissions.set(
                Permission.objects.filter(
                    content_type__app_label="leads", codename__in=["view_lead", "retry_sheet_sync"]
                )
            )
        self.stdout.write("Reference data is in place.")
