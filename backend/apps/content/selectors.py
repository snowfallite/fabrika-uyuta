"""Read side of content: plain dicts shaped as the section 7 DTOs."""

from typing import Any


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
    # Stub until S1-09 (slots), S2-06 (categories), S2-07 (featured).
    return {
        "slots": {"hero": None, "about": None, "material_ldsp": None, "material_mdf": None},
        "categories": [],
        "featured": [],
    }


def get_category_detail(slug: str) -> dict[str, Any] | None:
    # Stub until S2-08: every slug is unknown.
    return None
