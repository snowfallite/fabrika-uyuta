"""Batch upload into a category gallery (tech.md, S2-09): all files or none."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import transaction
from django.db.models import Max

from apps.content.models import Category, GalleryItem
from apps.content.services.images import (
    delete_image_folder,
    image_folder,
    ingest_image,
    validate_image_file,
)

MAX_FILES = 20
NO_FILES = "Выберите фото."
TOO_MANY = f"Не больше {MAX_FILES} файлов за раз."


def upload_gallery_batch(category: Category, files: Sequence[File[Any]]) -> list[GalleryItem]:
    """Validate every file first, then ingest in selection order after the current last work."""
    if not files:
        raise ValidationError(NO_FILES)
    if len(files) > MAX_FILES:
        raise ValidationError(TOO_MANY)
    problems = []
    for file in files:
        try:
            validate_image_file(file)
        except ValidationError as exc:
            problems.append(f"{file.name}: {exc.messages[0]}")
    if problems:
        raise ValidationError(problems)

    created: list[GalleryItem] = []
    try:
        with transaction.atomic():
            last = category.gallery_items.aggregate(last=Max("position"))["last"] or 0
            for offset, file in enumerate(files, start=1):
                item = GalleryItem(category=category, position=last + offset, is_featured=False)
                ingest_image(item, file)
                created.append(item)
                item.save()
    except Exception:
        # A file that passed the header checks can still fail to decode: leave no files behind.
        for item in created:
            folder = image_folder(item.image.name)
            if folder:
                delete_image_folder(folder)
        raise
    return created
