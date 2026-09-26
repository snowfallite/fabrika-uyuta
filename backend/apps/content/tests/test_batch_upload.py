"""S2-09: batch upload of photos into a category gallery."""

from pathlib import Path
from typing import Any

import pytest
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client
from django.urls import reverse

from apps.content.models import Category, GalleryItem
from apps.content.services.batch_upload import TOO_MANY
from apps.content.services.images import TOO_SMALL
from apps.content.tests.imagegen import files_under, image_bytes, upload

pytestmark = pytest.mark.django_db


@pytest.fixture
def kitchens() -> Category:
    call_command("sync_reference_data")
    return Category.objects.get(slug="kitchens")


def owner() -> Client:
    client = Client()
    client.force_login(User.objects.create_superuser("owner", "owner@example.com", "x"))
    return client


def colored(index: int) -> SimpleUploadedFile:
    # Distinct solid colors (lossless PNG) make the stored order checkable via image_color.
    color = (index * 10, 100, 200)
    return upload(image_bytes(900, 800, fmt="PNG", color=color), f"photo-{index:02d}.png")


def post(client: Client, category: Category, files: list[SimpleUploadedFile]) -> Any:
    return client.post(
        reverse("admin:content_category_upload", args=[category.pk]), {"photos": files}
    )


def test_ac1_twenty_files_become_twenty_works_in_order(kitchens: Category) -> None:
    GalleryItem.objects.create(category=kitchens, image="content/x/master.jpg", position=7)

    response = post(owner(), kitchens, [colored(i) for i in range(20)])

    assert response.status_code == 302
    works = list(kitchens.gallery_items.exclude(position=7).order_by("position"))
    assert [work.position for work in works] == list(range(8, 28))
    assert [work.image_color for work in works] == [f"#{i * 10:02x}64c8" for i in range(20)]
    assert all(work.is_published and not work.is_featured for work in works)
    assert all(work.image_variants for work in works)


def test_ac2_twenty_one_files_are_refused(kitchens: Category, media_root: Path) -> None:
    response = post(owner(), kitchens, [colored(i) for i in range(21)])
    assert response.status_code == 200
    assert TOO_MANY in response.content.decode()
    assert not GalleryItem.objects.exists()
    assert files_under(media_root) == []


def test_ac3_one_bad_file_rejects_the_batch_by_name(kitchens: Category, media_root: Path) -> None:
    files = [colored(i) for i in range(5)]
    files.insert(2, upload(image_bytes(600, 400), "tiny.jpg"))

    response = post(owner(), kitchens, files)

    page = response.content.decode()
    assert "tiny.jpg" in page and TOO_SMALL in page
    assert "photo-00.png" not in page
    assert not GalleryItem.objects.exists()
    assert files_under(media_root) == []


def test_upload_needs_change_permission(kitchens: Category) -> None:
    viewer = User.objects.create_user("viewer", is_staff=True)
    viewer.groups.add(Group.objects.get(name="Заявки"))
    client = Client()
    client.force_login(viewer)
    assert post(client, kitchens, [colored(1)]).status_code == 403


def test_category_page_links_to_the_upload(kitchens: Category) -> None:
    page = owner().get(reverse("admin:content_category_change", args=[kitchens.pk]))
    assert reverse("admin:content_category_upload", args=[kitchens.pk]) in page.content.decode()
