from typing import Any

from django.utils import timezone

from apps.content.models import Category
from apps.core.enums import CATEGORY_SEED, ProductKind
from apps.leads.models import Lead


def make_categories() -> None:
    """The six seeded categories (tech.md, 15.2). Since v15 a lead needs one to exist."""
    Category.objects.bulk_create(
        Category(slug=slug, title=title, position=position)
        for position, (slug, title) in enumerate(CATEGORY_SEED)
    )


def make_lead(**overrides: Any) -> Lead:
    """Fictitious lead data only (tech.md, 13.1)."""
    fields: dict[str, Any] = {
        "name": "Тестовый Клиент",
        "phone": "+79990000001",
        "product": ProductKind.KITCHENS,
        "consent_version": "2026-09-25",
        "consent_at": timezone.now(),
    } | overrides
    # The snapshot follows the kind unless the caller pins it; "" models a lead from before v15.
    fields.setdefault("product_label", dict(ProductKind.choices).get(fields["product"], ""))
    return Lead.objects.create(**fields)
