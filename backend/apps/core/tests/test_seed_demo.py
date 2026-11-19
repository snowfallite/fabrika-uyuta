"""S1-08: seed_demo (tech.md, 15.3)."""

import random
import re
from pathlib import Path
from typing import Any

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.content.models import Category, GalleryItem, SiteImage, SiteSettings
from apps.core.enums import SheetStatus
from apps.leads.messenger.fake import FakeMessengerClient
from apps.leads.models import Lead
from apps.leads.sheets.fake import FakeSheetsClient
from apps.leads.worker import run_cycle

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def media_root(tmp_path: Path, settings: Any) -> Path:
    settings.MEDIA_ROOT = tmp_path / "media"
    return Path(settings.MEDIA_ROOT)


def seed(*args: str) -> None:
    call_command("sync_reference_data")
    call_command("seed_demo", *args)


def counts() -> dict[str, int]:
    return {
        "slots_with_photo": SiteImage.objects.exclude(image="").count(),
        "covers": Category.objects.exclude(image="").count(),
        "gallery": GalleryItem.objects.count(),
        "featured": GalleryItem.objects.filter(is_featured=True).count(),
        "leads": Lead.objects.count(),
    }


EXPECTED = {"slots_with_photo": 4, "covers": 6, "gallery": 12, "featured": 4, "leads": 3}


def test_ac1_seed_twice_keeps_counts() -> None:
    seed()
    first = counts()
    names = set(SiteImage.objects.values_list("image", flat=True))
    seed()
    assert counts() == first == EXPECTED
    assert set(SiteImage.objects.values_list("image", flat=True)) == names


def test_ac1_reset_recreates_demo_data() -> None:
    seed()
    old_names = set(SiteImage.objects.values_list("image", flat=True))
    SiteSettings.objects.filter(id=1).update(email="changed@example.ru")

    call_command("seed_demo", "--reset")

    assert counts() == EXPECTED
    assert set(SiteImage.objects.values_list("image", flat=True)).isdisjoint(old_names)
    assert SiteSettings.objects.get(id=1).email == "info@example.ru"


def test_ac2_seed_fills_everything_with_pipeline_images(media_root: Path) -> None:
    seed()
    assert counts() == EXPECTED
    images = [*SiteImage.objects.all(), *Category.objects.all(), *GalleryItem.objects.all()]
    for image in images:
        assert image.image_variants, image
        assert re.fullmatch(r"#[0-9a-f]{6}", image.image_color)
        for name in image.image_variants.values():
            assert (media_root / name).exists()
    contacts = SiteSettings.objects.get(id=1)
    assert contacts.phone and contacts.email and contacts.address and contacts.work_hours
    assert contacts.max_phone
    # VK is its own field since v9; social_links stays for other networks.
    assert contacts.vk_url
    assert contacts.social_links.count() == 0
    statuses = sorted(Lead.objects.values_list("sheet_status", flat=True))
    assert statuses == sorted([SheetStatus.PENDING, SheetStatus.SENT, SheetStatus.FAILED])
    # v15: a demo lead carries the slug and the title of its category.
    slugs = set(Category.objects.values_list("slug", flat=True))
    for product, label in Lead.objects.values_list("product", "product_label"):
        assert product in slugs
        assert label


def test_ac3_production_refuses_and_writes_nothing(settings: Any, media_root: Path) -> None:
    call_command("sync_reference_data")
    settings.APP_ENV = "production"
    with pytest.raises(CommandError):
        call_command("seed_demo")
    assert counts() == {k: 0 for k in EXPECTED}
    assert not media_root.exists() or not any(media_root.rglob("*.*"))


def test_ac4_pending_demo_lead_reaches_the_fake_sheet(tmp_path: Path) -> None:
    seed()
    sheet = tmp_path / "fake-sheet.jsonl"
    run_cycle(FakeSheetsClient(sheet), FakeMessengerClient(), random.Random(3))  # noqa: S311
    pending = Lead.objects.get(public_id="8f1d9c1e-0000-4000-8000-000000000001")
    assert [row[0] for row in FakeSheetsClient(sheet).rows()] == [str(pending.public_id)]
    pending.refresh_from_db()
    assert pending.sheet_status == SheetStatus.SENT
