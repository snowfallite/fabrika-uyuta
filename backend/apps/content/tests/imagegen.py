"""Test images generated in memory: no binary fixtures (tech.md, section 17)."""

from io import BytesIO
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def image_bytes(
    width: int,
    height: int,
    fmt: str = "JPEG",
    color: tuple[int, int, int] = (160, 120, 80),
    exif: Image.Exif | None = None,
) -> bytes:
    image = Image.new("RGB", (width, height), color)
    buffer = BytesIO()
    image.save(buffer, fmt, **({"exif": exif} if exif is not None else {}))
    return buffer.getvalue()


def upload(data: bytes, name: str = "photo.jpg") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, data, content_type="application/octet-stream")


def files_under(root: Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
