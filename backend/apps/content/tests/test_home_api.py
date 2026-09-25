"""GET /api/v1/home/: slots (S1-09)."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client
from django.urls import reverse

from apps.content.models import SiteImage
from apps.content.services.images import ingest_image
from apps.content.tests.imagegen import image_bytes, upload
from apps.core.enums import SiteImageSlot

pytestmark = pytest.mark.django_db
MaxQueries = Callable[[int], AbstractContextManager[Any]]


@pytest.fixture(autouse=True)
def reference_rows() -> None:
    call_command("sync_reference_data")


def get_home(client: Client, settings: Any) -> dict[str, Any]:
    response = client.get(
        "/api/v1/home/", headers={"X-Internal-Token": settings.INTERNAL_API_TOKEN}
    )
    assert response.status_code == 200
    assert response["Cache-Control"] == "no-store"
    data: dict[str, Any] = response.json()
    return data


def test_ac1_hero_uploaded_in_admin_shows_up_with_all_variants(
    client: Client, settings: Any
) -> None:
    admin_client = Client()
    admin_client.force_login(User.objects.create_superuser("owner", "owner@example.com", "x"))
    hero = SiteImage.objects.get(slot=SiteImageSlot.HERO)
    response = admin_client.post(
        reverse("admin:content_siteimage_change", args=[hero.pk]),
        {"alt": "Кухня из дуба", "image": upload(image_bytes(2400, 1600))},
    )
    assert response.status_code == 302

    asset = get_home(client, settings)["slots"]["hero"]

    hero.refresh_from_db()
    folder = hero.image.name.rsplit("/", 1)[0]
    assert asset == {
        "url": f"/media/{folder}/w1920.webp",
        "srcset": ", ".join(f"/media/{folder}/w{w}.webp {w}w" for w in (640, 1280, 1920)),
        "width": 1920,
        "height": 1280,
        "alt": "Кухня из дуба",
        "color": hero.image_color,
    }


def test_ac2_empty_slots_are_null(client: Client, settings: Any) -> None:
    slots = get_home(client, settings)["slots"]
    assert slots == {"hero": None, "about": None, "material_ldsp": None, "material_mdf": None}


@pytest.mark.parametrize("slot", SiteImageSlot.values)
def test_empty_alt_falls_back_to_the_slot_label(client: Client, settings: Any, slot: str) -> None:
    image = SiteImage.objects.get(slot=slot)
    ingest_image(image, upload(image_bytes(1000, 800)))
    image.save()
    asset = get_home(client, settings)["slots"][slot]
    assert asset["alt"] == f"Фабрика Уюта: {SiteImageSlot(slot).label}"


def test_ac4_home_makes_at_most_four_queries(
    client: Client, settings: Any, django_assert_max_num_queries: MaxQueries
) -> None:
    for image in SiteImage.objects.all():
        ingest_image(image, upload(image_bytes(1000, 800)))
        image.save()
    with django_assert_max_num_queries(4):
        get_home(client, settings)


def test_slot_admin_has_no_add_or_delete_and_fixed_slot() -> None:
    admin_client = Client()
    admin_client.force_login(User.objects.create_superuser("owner", "owner@example.com", "x"))
    hero = SiteImage.objects.get(slot=SiteImageSlot.HERO)
    assert admin_client.get(reverse("admin:content_siteimage_add")).status_code == 403
    assert (
        admin_client.get(reverse("admin:content_siteimage_delete", args=[hero.pk])).status_code
        == 403
    )
    page = admin_client.get(reverse("admin:content_siteimage_change", args=[hero.pk]))
    assert 'name="slot"' not in page.content.decode()
