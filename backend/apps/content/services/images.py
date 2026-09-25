"""Image pipeline (tech.md, section 9): validate, normalize, master JPEG and WebP variants."""

from __future__ import annotations

import re
import shutil
import uuid
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import Any, Final

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from PIL import Image, ImageOps, UnidentifiedImageError

from apps.content.models import ImageFieldsMixin

TARGET_WIDTHS: Final = (640, 1280, 1920)
MASTER_MAX_SIDE: Final = 2560
MAX_FILE_BYTES: Final = 20 * 1024 * 1024
MIN_LONG_SIDE: Final = 800
MAX_PIXELS: Final = 40_000_000
ALLOWED_FORMATS: Final = frozenset({"JPEG", "PNG", "WEBP"})
FOLDER_RE: Final = re.compile(
    r"^content/[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[0-9a-f]{4}-[0-9a-f]{12}$"
)

# Pillow's own decompression bomb guard follows our limit.
Image.MAX_IMAGE_PIXELS = MAX_PIXELS

WRONG_FORMAT = "Загрузите фото в формате JPEG, PNG или WebP."
TOO_BIG_FILE = "Файл больше 20 МБ."
TOO_MANY_PIXELS = "Фото больше 40 мегапикселей."
TOO_SMALL = "Фото меньше 800 px по длинной стороне."


def plan_variants(width: int) -> list[int]:
    """Variant widths for a master width: the targets below it plus min(width, 1920)."""
    return sorted({t for t in TARGET_WIDTHS if t < width} | {min(width, TARGET_WIDTHS[-1])})


def fit_within(width: int, height: int, max_side: int) -> tuple[int, int]:
    """Scale down so the long side fits max_side; never upscale."""
    longest = max(width, height)
    if longest <= max_side:
        return width, height
    scale = max_side / longest
    return max(1, round(width * scale)), max(1, round(height * scale))


def average_color_hex(image: Image.Image) -> str:
    """Placeholder color: the image averaged down to one pixel."""
    pixel = image.convert("RGB").resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))
    red, green, blue = pixel if isinstance(pixel, tuple) else (0, 0, 0)
    return f"#{red:02x}{green:02x}{blue:02x}"


def validate_image_file(file: File[Any]) -> None:
    """Reject files the pipeline must not touch; messages go straight to the admin."""
    if (file.size or 0) > MAX_FILE_BYTES:
        raise ValidationError(TOO_BIG_FILE)
    try:
        file.seek(0)
        with Image.open(file) as image:
            fmt, (width, height) = image.format, image.size
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValidationError(WRONG_FORMAT) from exc
    finally:
        file.seek(0)
    if fmt not in ALLOWED_FORMATS:
        raise ValidationError(WRONG_FORMAT)
    if width * height > MAX_PIXELS:
        raise ValidationError(TOO_MANY_PIXELS)
    if max(width, height) < MIN_LONG_SIDE:
        raise ValidationError(TOO_SMALL)


def image_folder(name: str) -> str | None:
    """The uuid folder of a pipeline file; None for anything else, so nothing else gets deleted."""
    folder = str(PurePosixPath(name).parent)
    return folder if FOLDER_RE.match(folder) else None


def delete_image_folder(folder: str) -> None:
    if FOLDER_RE.match(folder):
        shutil.rmtree(Path(settings.MEDIA_ROOT) / folder, ignore_errors=True)


def ingest_image(instance: ImageFieldsMixin, file: File[Any]) -> None:
    """Write master and variants to a fresh folder and fill the image fields of instance.

    The previous folder goes away only after the surrounding transaction commits.
    """
    validate_image_file(file)
    with Image.open(file) as probe:
        probe.verify()
    file.seek(0)
    with Image.open(file) as source:
        icc_profile = source.info.get("icc_profile")
        upright = ImageOps.exif_transpose(source) or source
        rgb = _to_rgb(upright)

    master = rgb.resize(fit_within(*rgb.size, MASTER_MAX_SIDE), Image.Resampling.LANCZOS)
    folder = f"content/{uuid.uuid4()}"
    try:
        master_name = _save(
            f"{folder}/master.jpg",
            master,
            "JPEG",
            quality=88,
            progressive=True,
            icc_profile=icc_profile,
        )
        variants: dict[str, str] = {}
        for width in plan_variants(master.width):
            height = max(1, round(master.height * width / master.width))
            variant = master.resize((width, height), Image.Resampling.LANCZOS)
            variants[str(width)] = _save(
                f"{folder}/w{width}.webp", variant, "WEBP", quality=80, icc_profile=icc_profile
            )
    except Exception:
        delete_image_folder(folder)
        raise

    _schedule_old_folder_removal(instance)
    instance.image = master_name
    instance.image_width, instance.image_height = master.size
    instance.image_variants = variants
    instance.image_color = average_color_hex(master)


def clear_image(instance: ImageFieldsMixin) -> None:
    """The admin "Очистить" checkbox: empty fields now, delete files after commit."""
    _schedule_old_folder_removal(instance)
    instance.image = ""
    instance.image_width = instance.image_height = None
    instance.image_variants = {}
    instance.image_color = ""


def schedule_folder_removal(name: str) -> None:
    folder = image_folder(name)
    if folder:
        transaction.on_commit(lambda: delete_image_folder(folder))


def _schedule_old_folder_removal(instance: ImageFieldsMixin) -> None:
    # The instance may already hold the uploaded file, so the stored name comes from the database.
    if instance.pk is None:
        return
    stored = type(instance)._default_manager.filter(pk=instance.pk).values_list("image", flat=True)
    old_name = stored.first()
    if old_name:
        schedule_folder_removal(old_name)


def _to_rgb(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "LA"} or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        flattened = Image.new("RGB", rgba.size, (255, 255, 255))
        flattened.paste(rgba, mask=rgba.getchannel("A"))
        return flattened
    return image.convert("RGB")


def _save(name: str, image: Image.Image, fmt: str, **params: Any) -> str:
    buffer = BytesIO()
    # No exif argument: EXIF, GPS included, never reaches the saved files.
    image.save(buffer, fmt, **{k: v for k, v in params.items() if v is not None})
    return default_storage.save(name, ContentFile(buffer.getvalue()))


def to_image_asset(instance: ImageFieldsMixin, fallback_alt: str) -> dict[str, Any] | None:
    """ImageAsset DTO (tech.md, section 7): widest variant in url, all variants in srcset."""
    variants = instance.image_variants or {}
    if not instance.image or not variants or not instance.image_width or not instance.image_height:
        return None
    widths = sorted(int(width) for width in variants)
    widest = widths[-1]
    return {
        "url": default_storage.url(variants[str(widest)]),
        "srcset": ", ".join(f"{default_storage.url(variants[str(w)])} {w}w" for w in widths),
        "width": widest,
        "height": max(1, round(instance.image_height * widest / instance.image_width)),
        "alt": instance.alt or fallback_alt,
        "color": instance.image_color,
    }
