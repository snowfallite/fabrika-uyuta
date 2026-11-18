"""S2-16: the content manager adds, edits and deletes categories in the admin."""

from typing import Any

import pytest
from django.contrib.admin.sites import site
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, RequestFactory
from django.urls import reverse

from apps.content.admin import CategoryAdmin
from apps.content.models import Category, GalleryItem
from apps.content.tests.test_home_gallery import item

pytestmark = pytest.mark.django_db

ADD = "admin:content_category_add"
CHANGE = "admin:content_category_change"
DELETE = "admin:content_category_delete"

FORM: dict[str, str] = {
    "slug": "kids",
    "title": "Детская мебель",
    "short_description": "Кровати, столы и системы хранения для детской.",
    "description": "",
    "alt": "",
    "seo_title": "",
    "seo_description": "",
    "position": "9",
    "is_published": "on",
    "gallery_items-TOTAL_FORMS": "0",
    "gallery_items-INITIAL_FORMS": "0",
    "gallery_items-MIN_NUM_FORMS": "0",
    "gallery_items-MAX_NUM_FORMS": "1000",
}


@pytest.fixture
def owner() -> Client:
    call_command("sync_reference_data")
    client = Client()
    client.force_login(User.objects.create_superuser("owner", "owner@example.com", "x"))
    return client


def api(client: Client, settings: Any, path: str) -> Any:
    return client.get(path, headers={"X-Internal-Token": settings.INTERNAL_API_TOKEN})


def test_ac1_admin_creates_a_category_that_the_api_serves(owner: Client, settings: Any) -> None:
    response = owner.post(reverse(ADD), FORM)
    assert response.status_code == 302
    category = Category.objects.get(slug="kids")
    assert category.title == "Детская мебель"

    home = api(Client(), settings, "/api/v1/home/").json()
    assert "kids" in [entry["slug"] for entry in home["categories"]]
    assert api(Client(), settings, "/api/v1/categories/kids/").status_code == 200


def test_ac1_title_prepopulates_the_slug_only_while_adding(owner: Client) -> None:
    admin = site._registry[Category]
    assert isinstance(admin, CategoryAdmin)
    request = RequestFactory().get("/")
    assert admin.get_prepopulated_fields(request) == {"slug": ("title",)}
    assert admin.get_prepopulated_fields(request, Category.objects.get(slug="kitchens")) == {}


def test_ac3_a_duplicate_slug_is_refused(owner: Client) -> None:
    response = owner.post(reverse(ADD), {**FORM, "slug": "kitchens"})
    assert response.status_code == 200
    assert Category.objects.filter(slug="kitchens").count() == 1


@pytest.mark.parametrize("slug", ["детская мебель", "kids furniture", "kids/furniture"])
def test_ac3_a_slug_that_breaks_the_url_is_refused(owner: Client, slug: str) -> None:
    response = owner.post(reverse(ADD), {**FORM, "slug": slug})
    assert response.status_code == 200
    assert not Category.objects.filter(title="Детская мебель").exists()


def test_ac3_the_slug_of_an_existing_category_stays(owner: Client) -> None:
    category = Category.objects.get(slug="office")
    owner.post(reverse(CHANGE, args=[category.pk]), {**FORM, "slug": "renamed"})
    category.refresh_from_db()
    assert category.slug == "office"
    assert category.title == "Детская мебель"


def test_ac4_a_category_without_works_is_deleted(owner: Client) -> None:
    category = Category.objects.get(slug="office")
    response = owner.post(reverse(DELETE, args=[category.pk]), {"post": "yes"})
    assert response.status_code == 302
    assert not Category.objects.filter(slug="office").exists()


def test_ac4_a_category_with_works_is_kept(owner: Client) -> None:
    category = Category.objects.get(slug="office")
    work = item(category, 1, title="Шкаф для офиса")
    response = owner.post(reverse(DELETE, args=[category.pk]), {"post": "yes"})
    assert response.status_code == 200
    assert "Шкаф для офиса" in response.content.decode()
    assert Category.objects.filter(slug="office").exists()
    assert GalleryItem.objects.filter(pk=work.pk).exists()
