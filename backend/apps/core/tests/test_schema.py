"""S1-04 AC1: the API schema declares every operation and DTO of tech.md, section 7."""

from typing import Any

import pytest
from drf_spectacular.generators import SchemaGenerator

OPERATIONS = {
    ("/api/v1/site-settings/", "get"): {"200", "403"},
    ("/api/v1/home/", "get"): {"200", "403"},
    ("/api/v1/categories/{slug}/", "get"): {"200", "403", "404"},
    ("/api/v1/leads/", "post"): {"201", "400", "403", "429"},
}
COMPONENTS = {
    "ImageAsset",
    "SocialLink",
    "SiteSettings",
    "CategorySummary",
    "CategoryDetail",
    "GalleryItem",
    "HomeSlots",
    "HomeContent",
    "LeadCreateRequest",
    "LeadCreated",
    "ProductKindEnum",
    "CategorySlugEnum",
}


@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    result: dict[str, Any] = SchemaGenerator().get_schema(request=None, public=True)
    return result


def test_ac1_every_operation_with_its_status_codes(schema: dict[str, Any]) -> None:
    declared = {
        (path, method): set(operation["responses"])
        for path, item in schema["paths"].items()
        for method, operation in item.items()
    }
    assert declared == OPERATIONS


def test_ac1_components_use_exact_names(schema: dict[str, Any]) -> None:
    assert set(schema["components"]["schemas"]) >= COMPONENTS


def test_ac1_kind_and_category_fields_reference_enums(schema: dict[str, Any]) -> None:
    schemas = schema["components"]["schemas"]
    product_ref = "#/components/schemas/ProductKindEnum"
    slug_ref = "#/components/schemas/CategorySlugEnum"
    assert schemas["LeadCreateRequest"]["properties"]["product"] == {"$ref": product_ref}
    assert schemas["CategorySummary"]["properties"]["slug"] == {"$ref": slug_ref}
    assert schemas["CategoryDetail"]["properties"]["slug"] == {"$ref": slug_ref}
    assert schemas["GalleryItem"]["properties"]["category"] == {"$ref": slug_ref}
    assert schemas["ProductKindEnum"]["enum"] == [
        "kitchens",
        "kitchen-tables",
        "wardrobes",
        "sliding-wardrobes",
        "office",
        "other",
    ]
    assert "other" not in schemas["CategorySlugEnum"]["enum"]


def test_ac1_internal_token_security_scheme(schema: dict[str, Any]) -> None:
    scheme = schema["components"]["securitySchemes"]["InternalToken"]
    assert scheme == {"type": "apiKey", "in": "header", "name": "X-Internal-Token"}
    for item in schema["paths"].values():
        for operation in item.values():
            assert operation["security"] == [{"InternalToken": []}]
