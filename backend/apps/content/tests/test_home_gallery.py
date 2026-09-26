"""S2-07: featured works on the home page."""

from typing import Any

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client
from django.urls import reverse
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from apps.content.models import Category, GalleryItem
from apps.content.selectors import get_home_content

pytestmark = pytest.mark.django_db


def item(category: Category, n: int, **fields: Any) -> GalleryItem:
    """Pipeline-shaped image fields without files: the selector only reads them."""
    folder = f"content/00000000-0000-4000-8000-{n:012d}"
    return GalleryItem.objects.create(
        category=category,
        title=fields.pop("title", f"Работа {n}"),
        image=f"{folder}/master.jpg",
        image_width=1600,
        image_height=1200,
        image_variants={"640": f"{folder}/w640.webp", "1280": f"{folder}/w1280.webp"},
        image_color="#a07850",
        **fields,
    )


@pytest.fixture
def kitchens() -> Category:
    call_command("sync_reference_data")
    return Category.objects.get(slug="kitchens")


flags = st.lists(
    st.tuples(st.booleans(), st.booleans(), st.integers(0, 5)), min_size=0, max_size=16
)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=40)
@given(flags)
def test_ac1_featured_is_a_sorted_subset_of_published_featured(
    kitchens: Category, rows: list[tuple[bool, bool, int]]
) -> None:
    GalleryItem.objects.all().delete()
    for n, (featured, published, position) in enumerate(rows):
        item(kitchens, n, is_featured=featured, is_published=published, position=position)

    featured = get_home_content()["featured"]

    allowed = set(
        GalleryItem.objects.filter(is_featured=True, is_published=True).values_list("pk", flat=True)
    )
    ids = [entry["id"] for entry in featured]
    assert set(ids) <= allowed
    assert len(ids) == min(12, len(allowed))
    order = {
        pk: (pos, -created.timestamp())
        for pk, pos, created in GalleryItem.objects.values_list("pk", "position", "created_at")
    }
    assert [order[pk] for pk in ids] == sorted(order[pk] for pk in ids)


def test_featured_item_shape(kitchens: Category) -> None:
    work = item(kitchens, 1, title="", caption="Дуб", is_featured=True)
    [entry] = get_home_content()["featured"]
    assert entry["id"] == work.pk
    assert entry["category"] == "kitchens"
    assert (entry["title"], entry["caption"]) == ("", "Дуб")
    folder = work.image.name.rsplit("/", 1)[0]
    assert entry["image"]["url"] == f"/media/{folder}/w1280.webp"
    assert entry["image"]["alt"] == "Кухни под заказ"  # no title: category title


def test_gallery_admin_edits_flags_in_the_list(kitchens: Category) -> None:
    item(kitchens, 1)
    admin_client = Client()
    admin_client.force_login(User.objects.create_superuser("owner", "owner@example.com", "x"))
    page = admin_client.get(reverse("admin:content_galleryitem_changelist")).content.decode()
    for field in ("position", "is_published", "is_featured"):
        assert f'name="form-0-{field}"' in page
    category_page = admin_client.get(
        reverse("admin:content_category_change", args=[kitchens.pk])
    ).content.decode()
    assert "Работа 1" in category_page
