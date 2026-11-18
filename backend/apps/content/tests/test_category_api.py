"""S2-08: GET /api/v1/categories/{slug}/."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

import pytest
from django.core.management import call_command
from django.test import Client

from apps.content.models import Category, GalleryItem
from apps.content.tests.test_home_gallery import item

pytestmark = pytest.mark.django_db
MaxQueries = Callable[[int], AbstractContextManager[Any]]


@pytest.fixture(autouse=True)
def reference_rows() -> None:
    call_command("sync_reference_data")


def get(client: Client, settings: Any, slug: str) -> Any:
    return client.get(
        f"/api/v1/categories/{slug}/", headers={"X-Internal-Token": settings.INTERNAL_API_TOKEN}
    )


def test_ac1_published_category_with_its_published_gallery(client: Client, settings: Any) -> None:
    kitchens = Category.objects.get(slug="kitchens")
    Category.objects.filter(pk=kitchens.pk).update(
        short_description="Кухонные гарнитуры", description="Первый абзац.\n\nВторой абзац."
    )
    late = item(kitchens, 1, title="Поздняя", position=5)
    early = item(kitchens, 2, title="Ранняя", position=1)
    item(kitchens, 3, title="Скрытая", position=0, is_published=False)
    item(Category.objects.get(slug="office"), 4, title="Чужая")

    response = get(client, settings, "kitchens")

    assert response.status_code == 200
    assert response["Cache-Control"] == "no-store"
    data = response.json()
    assert (data["slug"], data["title"]) == ("kitchens", "Кухни под заказ")
    assert data["description"] == "Первый абзац.\n\nВторой абзац."
    assert [work["id"] for work in data["gallery"]] == [early.pk, late.pk]
    assert data["cover"] is None


def test_ac3_seo_fields_fall_back_to_title_and_short_description(
    client: Client, settings: Any
) -> None:
    Category.objects.filter(slug="office").update(short_description="Для офиса")
    Category.objects.filter(slug="wardrobes").update(
        seo_title="Шкафы на заказ в Вологде", seo_description="Шкафы по размерам"
    )
    office = get(client, settings, "office").json()
    wardrobes = get(client, settings, "wardrobes").json()
    assert (office["seo_title"], office["seo_description"]) == ("Офисная мебель", "Для офиса")
    assert (wardrobes["seo_title"], wardrobes["seo_description"]) == (
        "Шкафы на заказ в Вологде",
        "Шкафы по размерам",
    )


@pytest.mark.parametrize("slug", ["spaceship", "kids", "KITCHENS"])
def test_ac2_unknown_slug_is_404(client: Client, settings: Any, slug: str) -> None:
    response = get(client, settings, slug)
    assert response.status_code == 404
    assert set(response.json()) == {"detail"}


def test_ac2_hidden_category_is_404(client: Client, settings: Any) -> None:
    Category.objects.filter(slug="office").update(is_published=False)
    assert get(client, settings, "office").status_code == 404


def test_ac5_at_most_three_queries(
    client: Client, settings: Any, django_assert_max_num_queries: MaxQueries
) -> None:
    kitchens = Category.objects.get(slug="kitchens")
    for n in range(5):
        item(kitchens, n)
    with django_assert_max_num_queries(3):
        assert get(client, settings, "kitchens").status_code == 200
    assert GalleryItem.objects.count() == 5
