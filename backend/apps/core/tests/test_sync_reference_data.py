"""S1-04 AC3: sync_reference_data is idempotent and keeps edits."""

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command

from apps.content.models import Category, SiteImage, SiteSettings

pytestmark = pytest.mark.django_db


def counts() -> tuple[int, int, int, int]:
    return (
        Category.objects.count(),
        SiteImage.objects.count(),
        SiteSettings.objects.count(),
        Group.objects.filter(name__in=["Контент", "Заявки"]).count(),
    )


def test_ac3_twice_gives_the_same_counts() -> None:
    call_command("sync_reference_data")
    assert counts() == (5, 4, 1, 2)
    call_command("sync_reference_data")
    assert counts() == (5, 4, 1, 2)


def test_ac3_existing_values_are_not_overwritten() -> None:
    call_command("sync_reference_data")
    Category.objects.filter(slug="kitchens").update(title="Кухни мечты", position=9)
    SiteSettings.objects.filter(id=1).update(address="Вологда, ул. Примерная, 1")
    leads_group = Group.objects.get(name="Заявки")
    leads_group.permissions.clear()

    call_command("sync_reference_data")

    kitchens = Category.objects.get(slug="kitchens")
    assert (kitchens.title, kitchens.position) == ("Кухни мечты", 9)
    assert SiteSettings.objects.get(id=1).address == "Вологда, ул. Примерная, 1"
    assert not leads_group.permissions.exists()


def test_ac3_groups_get_their_permissions() -> None:
    call_command("sync_reference_data")
    content = set(Group.objects.get(name="Контент").permissions.values_list("codename", flat=True))
    leads = set(Group.objects.get(name="Заявки").permissions.values_list("codename", flat=True))
    for model in ["category", "galleryitem", "siteimage", "sitesettings", "sociallink"]:
        assert {f"add_{model}", f"change_{model}", f"delete_{model}", f"view_{model}"} <= content
    assert leads == {"view_lead", "retry_sheet_sync"}
