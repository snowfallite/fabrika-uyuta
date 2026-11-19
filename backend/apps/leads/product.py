"""Name of the kind a lead asked for (tech.md, section 6)."""

from apps.core.enums import ProductKind
from apps.leads.models import Lead


def product_label(lead: Lead) -> str:
    """The snapshot taken when the lead arrived.

    Leads made before v15 carry no snapshot: their slug came from a closed enum, so the enum
    still labels them, and a slug it does not know goes out as it is. Data migrations are out
    (tech.md, 15.1), so this fallback is what keeps the archive readable.
    """
    if lead.product_label:
        return lead.product_label
    try:
        return ProductKind(lead.product).label
    except ValueError:
        return lead.product
