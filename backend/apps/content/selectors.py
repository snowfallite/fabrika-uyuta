"""Read side of content: plain dicts shaped as the section 7 DTOs."""

from typing import Any

from apps.content.models import SiteImage
from apps.content.services.images import to_image_asset
from apps.core.enums import SiteImageSlot


def get_site_settings() -> dict[str, Any]:
    # Stub until S2-10.
    return {
        "phone": "",
        "phone_display": "",
        "email": "",
        "address": "",
        "work_hours": "",
        "map_url": "",
        "social_links": [],
    }


def get_home_content() -> dict[str, Any]:
    # categories: stub until S2-06; featured: stub until S2-07.
    return {"slots": _slots(), "categories": [], "featured": []}


def _slots() -> dict[str, dict[str, Any] | None]:
    images = {image.slot: image for image in SiteImage.objects.all()}
    return {
        slot: to_image_asset(images[slot], f"Фабрика Уюта: {label}") if slot in images else None
        for slot, label in SiteImageSlot.choices
    }


def get_category_detail(slug: str) -> dict[str, Any] | None:
    # Stub until S2-08: every slug is unknown.
    return None
