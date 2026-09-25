"""S1-06: image pipeline (tech.md, section 9)."""

import re
from collections.abc import Callable
from contextlib import AbstractContextManager
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import Client
from django.urls import reverse
from hypothesis import given
from hypothesis import strategies as st
from PIL import ExifTags, Image

from apps.content.models import Category, GalleryItem, SiteImage
from apps.content.services.images import (
    TOO_BIG_FILE,
    TOO_MANY_PIXELS,
    TOO_SMALL,
    WRONG_FORMAT,
    average_color_hex,
    clear_image,
    fit_within,
    ingest_image,
    plan_variants,
    to_image_asset,
    validate_image_file,
)
from apps.content.tests.imagegen import files_under, image_bytes, upload
from apps.core.enums import SiteImageSlot

HEX = re.compile(r"^#[0-9a-f]{6}$")
CaptureCallbacks = Callable[..., AbstractContextManager[list[Callable[[], Any]]]]


# Pure functions -------------------------------------------------------------------------------


@given(st.integers(min_value=1, max_value=20_000))
def test_plan_variants_properties(width: int) -> None:
    widths = plan_variants(width)
    assert widths
    assert widths == sorted(set(widths))
    assert widths[-1] == min(width, 1920)
    assert all(w <= width for w in widths)


@given(st.integers(1, 20_000), st.integers(1, 20_000), st.integers(1, 5_000))
def test_fit_within_properties(width: int, height: int, max_side: int) -> None:
    fitted_w, fitted_h = fit_within(width, height, max_side)
    if max(width, height) <= max_side:
        assert (fitted_w, fitted_h) == (width, height)
        return
    scale = max_side / max(width, height)
    assert max(fitted_w, fitted_h) <= max_side
    assert 1 <= fitted_w <= width and 1 <= fitted_h <= height
    assert abs(fitted_w - width * scale) <= 1 and abs(fitted_h - height * scale) <= 1


@given(
    st.tuples(st.integers(0, 255), st.integers(0, 255), st.integers(0, 255)),
    st.integers(1, 40),
    st.integers(1, 40),
)
def test_average_color_of_a_solid_image_is_its_color(
    rgb: tuple[int, int, int], width: int, height: int
) -> None:
    color = average_color_hex(Image.new("RGB", (width, height), rgb))
    assert color == "#{:02x}{:02x}{:02x}".format(*rgb)


@given(st.binary(min_size=12, max_size=12))
def test_average_color_is_always_hex(pixels: bytes) -> None:
    image = Image.frombytes("RGB", (2, 2), pixels)
    assert HEX.match(average_color_hex(image))


def test_ac2_variant_plans_never_upscale() -> None:
    assert plan_variants(2560) == [640, 1280, 1920]
    assert plan_variants(1500) == [640, 1280, 1500]
    assert plan_variants(600) == [600]


# Ingest ---------------------------------------------------------------------------------------


def slot(name: SiteImageSlot = SiteImageSlot.HERO) -> SiteImage:
    return SiteImage.objects.create(slot=name)


def exif_rotated_with_gps() -> Image.Exif:
    exif = Image.Exif()
    exif[ExifTags.Base.Orientation] = 6  # stored landscape, shown portrait
    exif[ExifTags.Base.GPSInfo] = {
        ExifTags.GPS.GPSLatitudeRef: "N",
        ExifTags.GPS.GPSLatitude: (59.0, 13.0, 0.0),
    }
    return exif


@pytest.mark.django_db
def test_ac1_large_jpeg_with_exif_and_gps(media_root: Path) -> None:
    data = image_bytes(4000, 3000, exif=exif_rotated_with_gps())
    with Image.open(BytesIO(data)) as source:
        assert ExifTags.Base.GPSInfo in source.getexif()  # the fixture really carries GPS

    image = slot()
    ingest_image(image, upload(data))
    image.save()

    assert re.fullmatch(r"content/[0-9a-f-]{36}/master\.jpg", image.image.name)
    with Image.open(media_root / image.image.name) as master:
        assert master.format == "JPEG"
        assert master.size == (1920, 2560)  # orientation applied, long side 2560
        assert dict(master.getexif()) == {}
    assert (image.image_width, image.image_height) == (1920, 2560)
    assert list(image.image_variants) == ["640", "1280", "1920"]
    for width, name in image.image_variants.items():
        with Image.open(media_root / name) as variant:
            assert variant.format == "WEBP"
            assert variant.width == int(width)
            assert variant.height == max(1, round(2560 * int(width) / 1920))
            assert dict(variant.getexif()) == {}
    assert HEX.match(image.image_color)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("size", "variants"), [((1500, 1000), ["640", "1280", "1500"]), ((600, 900), ["600"])]
)
def test_ac2_narrow_images_are_not_upscaled(
    size: tuple[int, int], variants: list[str], media_root: Path
) -> None:
    image = slot()
    ingest_image(image, upload(image_bytes(*size, fmt="PNG"), "photo.png"))
    assert (image.image_width, image.image_height) == size
    assert list(image.image_variants) == variants


def huge_pixel_png() -> bytes:
    buffer = BytesIO()
    Image.new("1", (8000, 5001)).save(buffer, "PNG")
    return buffer.getvalue()


def oversized_jpeg() -> bytes:
    # JPEG decoders ignore trailing bytes, so the header stays valid.
    small = image_bytes(1000, 800)
    return small + b"\0" * (20 * 1024 * 1024 + 1 - len(small))


INVALID = [
    (oversized_jpeg, TOO_BIG_FILE),
    (lambda: image_bytes(700, 500), TOO_SMALL),
    (huge_pixel_png, TOO_MANY_PIXELS),
    (lambda: image_bytes(1000, 1000, fmt="GIF"), WRONG_FORMAT),
    (lambda: b"not an image at all", WRONG_FORMAT),
]


@pytest.mark.django_db
@pytest.mark.filterwarnings("ignore::PIL.Image.DecompressionBombWarning")
@pytest.mark.parametrize(("make", "message"), INVALID)
def test_ac3_invalid_files_fail_in_russian_and_write_nothing(
    make: Callable[[], bytes], message: str, media_root: Path
) -> None:
    file = upload(make())
    with pytest.raises(ValidationError) as exc_info:
        validate_image_file(file)
    assert exc_info.value.messages == [message]
    with pytest.raises(ValidationError):
        ingest_image(slot(), file)
    assert files_under(media_root) == []


@pytest.mark.django_db
def test_ac3_admin_shows_the_error_and_writes_nothing(client: Client, media_root: Path) -> None:
    client.force_login(User.objects.create_superuser("owner", "owner@example.com", "x"))
    image = slot()
    response = client.post(
        reverse("admin:content_siteimage_change", args=[image.pk]),
        {"slot": image.slot, "alt": "", "image": upload(image_bytes(700, 500))},
    )
    assert response.status_code == 200
    assert TOO_SMALL in response.content.decode()
    assert files_under(media_root) == []


@pytest.mark.django_db
def test_ac4_admin_upload_goes_through_the_pipeline(client: Client, media_root: Path) -> None:
    client.force_login(User.objects.create_superuser("owner", "owner@example.com", "x"))
    image = slot()
    response = client.post(
        reverse("admin:content_siteimage_change", args=[image.pk]),
        {"slot": image.slot, "alt": "", "image": upload(image_bytes(1200, 900))},
    )
    assert response.status_code == 302
    image.refresh_from_db()
    assert list(image.image_variants) == ["640", "1200"]
    assert (media_root / image.image.name).exists()


def folder_of(image: SiteImage | GalleryItem, media_root: Path) -> Path:
    return (media_root / str(image.image.name)).parent


@pytest.mark.django_db
def test_ac4_replacing_removes_the_old_folder_after_commit(
    media_root: Path, django_capture_on_commit_callbacks: CaptureCallbacks
) -> None:
    image = slot()
    ingest_image(image, upload(image_bytes(1000, 800)))
    image.save()
    old = folder_of(image, media_root)

    with django_capture_on_commit_callbacks(execute=True):
        ingest_image(image, upload(image_bytes(900, 900)))
        image.save()
        assert old.exists()  # still there until commit

    assert not old.exists()
    assert folder_of(image, media_root).exists()


@pytest.mark.django_db
def test_ac4_rollback_keeps_the_old_files(
    media_root: Path, django_capture_on_commit_callbacks: CaptureCallbacks
) -> None:
    image = slot()
    ingest_image(image, upload(image_bytes(1000, 800)))
    image.save()
    old = folder_of(image, media_root)

    with (
        django_capture_on_commit_callbacks(execute=True) as callbacks,
        pytest.raises(RuntimeError),
        transaction.atomic(),
    ):
        ingest_image(image, upload(image_bytes(900, 900)))
        image.save()
        raise RuntimeError("simulated failure")

    assert callbacks == []
    assert old.exists()


@pytest.mark.django_db
def test_ac4_clearing_removes_the_folder(
    media_root: Path, django_capture_on_commit_callbacks: CaptureCallbacks
) -> None:
    image = slot()
    ingest_image(image, upload(image_bytes(1000, 800)))
    image.save()
    old = folder_of(image, media_root)

    with django_capture_on_commit_callbacks(execute=True):
        clear_image(image)
        image.save()

    assert not old.exists()
    image.refresh_from_db()
    assert (image.image.name, image.image_variants, image.image_color) == ("", {}, "")
    assert image.image_width is None


@pytest.mark.django_db
def test_ac4_deleting_the_record_removes_the_folder(
    media_root: Path, django_capture_on_commit_callbacks: CaptureCallbacks
) -> None:
    category = Category.objects.create(slug="kitchens", title="Кухни под заказ")
    item = GalleryItem(category=category)
    ingest_image(item, upload(image_bytes(1000, 800)))
    item.save()
    old = folder_of(item, media_root)

    with django_capture_on_commit_callbacks(execute=True):
        item.delete()

    assert not old.exists()


@pytest.mark.django_db
def test_image_asset_lists_variants_in_ascending_order(media_root: Path) -> None:
    image = slot()
    ingest_image(image, upload(image_bytes(3000, 2000)))
    asset = to_image_asset(image, "Фабрика Уюта: Главный экран")
    assert asset is not None
    folder = image.image.name.rsplit("/", 1)[0]
    assert asset["url"] == f"/media/{folder}/w1920.webp"
    assert asset["srcset"] == ", ".join(
        f"/media/{folder}/w{w}.webp {w}w" for w in (640, 1280, 1920)
    )
    assert (asset["width"], asset["height"]) == (1920, 1280)
    assert asset["alt"] == "Фабрика Уюта: Главный экран"
    assert HEX.match(asset["color"])


@pytest.mark.django_db
def test_image_asset_is_none_for_an_empty_slot() -> None:
    assert to_image_asset(slot(), "alt") is None
