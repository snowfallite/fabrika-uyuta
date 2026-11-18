"""S2-16 AC5: slugs travel as plain strings and every work carries its category title."""

from typing import Any

import pytest
from django.core.management import call_command
from django.test import Client
from drf_spectacular.generators import SchemaGenerator

from apps.content.models import Category
from apps.content.tests.test_home_gallery import item

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def reference_rows() -> None:
    call_command("sync_reference_data")


def get(client: Client, settings: Any, path: str) -> Any:
    return client.get(path, headers={"X-Internal-Token": settings.INTERNAL_API_TOKEN})


def test_ac5_home_serves_slugs_as_strings_with_category_titles(
    client: Client, settings: Any
) -> None:
    item(Category.objects.get(slug="kitchens"), 1, is_featured=True)
    data = get(client, settings, "/api/v1/home/").json()
    entry = data["featured"][0]
    assert entry["category"] == "kitchens"
    assert entry["category_title"] == "Кухни под заказ"
    assert all(isinstance(summary["slug"], str) for summary in data["categories"])


def test_ac5_a_custom_category_serves_its_own_title(client: Client, settings: Any) -> None:
    kids = Category.objects.create(slug="kids", title="Детская мебель", position=9)
    item(kids, 2, is_featured=True)
    data = get(client, settings, "/api/v1/home/").json()
    entry = next(work for work in data["featured"] if work["category"] == "kids")
    assert entry["category_title"] == "Детская мебель"


def test_ac5_category_detail_carries_the_title_too(client: Client, settings: Any) -> None:
    item(Category.objects.get(slug="kitchens"), 3)
    data = get(client, settings, "/api/v1/categories/kitchens/").json()
    assert data["gallery"][0]["category_title"] == "Кухни под заказ"


def test_ac5_the_schema_holds_no_category_enum() -> None:
    schema: dict[str, Any] = SchemaGenerator().get_schema(request=None, public=True)
    schemas = schema["components"]["schemas"]
    assert "CategorySlugEnum" not in schemas
    fields = [
        ("CategorySummary", "slug"),
        ("CategoryDetail", "slug"),
        ("GalleryItem", "category"),
        ("GalleryItem", "category_title"),
    ]
    for component, field in fields:
        assert schemas[component]["properties"][field]["type"] == "string"
