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
    "ProductOption",
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


def test_ac10_the_kind_is_a_string_and_the_schema_holds_no_enum(schema: dict[str, Any]) -> None:
    """S2-17: the kinds are categories now, so no enum pins them down (tech.md, section 7)."""
    schemas = schema["components"]["schemas"]
    assert schemas["LeadCreateRequest"]["properties"]["product"]["type"] == "string"
    assert [name for name in schemas if name.endswith("Enum")] == []


def test_ac7_site_settings_carry_the_kind_list(schema: dict[str, Any]) -> None:
    schemas = schema["components"]["schemas"]
    options = schemas["SiteSettings"]["properties"]["product_options"]
    assert options["items"] == {"$ref": "#/components/schemas/ProductOption"}
    assert set(schemas["ProductOption"]["properties"]) == {"value", "label"}


def test_ac1_internal_token_security_scheme(schema: dict[str, Any]) -> None:
    scheme = schema["components"]["securitySchemes"]["InternalToken"]
    assert scheme == {"type": "apiKey", "in": "header", "name": "X-Internal-Token"}
    for item in schema["paths"].values():
        for operation in item.values():
            assert operation["security"] == [{"InternalToken": []}]
