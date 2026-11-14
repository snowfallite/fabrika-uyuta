"""Read side of content: plain dicts shaped as the section 7 DTOs."""

from typing import Any

from apps.content.models import Category, GalleryItem, SiteImage, SiteSettings
from apps.content.services.images import to_image_asset
from apps.core.enums import SiteImageSlot
from apps.core.phone import format_phone_display


def get_site_settings() -> dict[str, Any]:
    row = (
        SiteSettings.objects.prefetch_related("social_links").filter(id=1).first() or SiteSettings()
    )
    links = row.social_links.all() if row.pk else []
    return {
        "phone": row.phone,
        "phone_display": format_phone_display(row.phone),
        "max_phone": row.max_phone,
        "max_phone_display": format_phone_display(row.max_phone),
        "email": row.email,
        "address": row.address,
        "work_hours": row.work_hours,
        "map_url": row.map_url,
        "social_links": [{"label": link.label, "url": link.url} for link in links],
    }


FEATURED_LIMIT = 12


def get_home_content() -> dict[str, Any]:
    return {"slots": _slots(), "categories": _categories(), "featured": _featured()}


def _category_summary(category: Category) -> dict[str, Any]:
    return {
        "slug": category.slug,
        "title": category.title,
        "short_description": category.short_description,
        "cover": to_image_asset(category, category.title),
    }


def _categories() -> list[dict[str, Any]]:
    return [_category_summary(c) for c in Category.objects.filter(is_published=True)]


def _slots() -> dict[str, dict[str, Any] | None]:
    images = {image.slot: image for image in SiteImage.objects.all()}
    return {
        slot: to_image_asset(images[slot], f"Фабрика Уюта: {label}") if slot in images else None
        for slot, label in SiteImageSlot.choices
    }


def get_category_detail(slug: str) -> dict[str, Any] | None:
    """A published category with its published works; None means 404."""
    category = Category.objects.filter(slug=slug, is_published=True).first()
    if category is None:
        return None
    works = (
        gallery_item(work, category) for work in category.gallery_items.filter(is_published=True)
    )
    return {
        **_category_summary(category),
        "description": category.description,
        "seo_title": category.seo_title or category.title,
        "seo_description": category.seo_description or category.short_description,
        "gallery": [work for work in works if work is not None],
    }


def gallery_item(item: GalleryItem, category: Category) -> dict[str, Any] | None:
    image = to_image_asset(item, item.title or category.title)
    if image is None:
        return None
    return {
        "id": item.pk,
        "category": category.slug,
        "title": item.title,
        "caption": item.caption,
        "image": image,
    }


def _featured() -> list[dict[str, Any]]:
    items = GalleryItem.objects.filter(is_featured=True, is_published=True).select_related(
        "category"
    )[:FEATURED_LIMIT]
    entries = (gallery_item(item, item.category) for item in items)
    return [entry for entry in entries if entry is not None]
