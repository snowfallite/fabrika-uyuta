"""S2-06: categories on the home page."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client
from django.urls import reverse

from apps.content.models import Category, GalleryItem, SiteImage
from apps.content.services.images import ingest_image
from apps.content.tests.imagegen import image_bytes, upload

pytestmark = pytest.mark.django_db
MaxQueries = Callable[[int], AbstractContextManager[Any]]


@pytest.fixture(autouse=True)
def reference_rows() -> None:
    call_command("sync_reference_data")


def home(client: Client, settings: Any) -> dict[str, Any]:
    response = client.get(
        "/api/v1/home/", headers={"X-Internal-Token": settings.INTERNAL_API_TOKEN}
    )
    assert response.status_code == 200
    data: dict[str, Any] = response.json()
    return data


def test_ac1_published_categories_in_position_order(client: Client, settings: Any) -> None:
    Category.objects.filter(slug="office").update(position=0)
    Category.objects.filter(slug="kitchens").update(position=9)
    Category.objects.filter(slug="wardrobes").update(is_published=False)

    slugs = [c["slug"] for c in home(client, settings)["categories"]]

    assert slugs == ["office", "kitchen-tables", "sliding-wardrobes", "kitchens"]


def test_ac2_category_without_cover_has_null_cover(client: Client, settings: Any) -> None:
    kitchens = Category.objects.get(slug="kitchens")
    kitchens.short_description = "Кухонные гарнитуры"
    ingest_image(kitchens, upload(image_bytes(1200, 1500)))
    kitchens.save()

    categories = {c["slug"]: c for c in home(client, settings)["categories"]}

    assert categories["office"]["cover"] is None
    cover = categories["kitchens"]["cover"]
    assert cover["alt"] == "Кухни под заказ"  # empty alt falls back to the title
    assert categories["kitchens"]["short_description"] == "Кухонные гарнитуры"


def test_ac4_home_stays_within_four_queries(
    client: Client, settings: Any, django_assert_max_num_queries: MaxQueries
) -> None:
    for image in [*SiteImage.objects.all(), *Category.objects.all()]:
        ingest_image(image, upload(image_bytes(900, 800)))
        image.save()
    item = GalleryItem(category=Category.objects.first(), is_featured=True)
    ingest_image(item, upload(image_bytes(900, 800)))
    item.save()
    with django_assert_max_num_queries(4):
        home(client, settings)


def test_category_admin_has_fixed_rows_and_inline_order() -> None:
    admin_client = Client()
    admin_client.force_login(User.objects.create_superuser("owner", "owner@example.com", "x"))
    assert admin_client.get(reverse("admin:content_category_add")).status_code == 403
    page = admin_client.get(reverse("admin:content_category_changelist")).content.decode()
    assert 'name="form-0-position"' in page
    assert 'name="form-0-is_published"' in page
