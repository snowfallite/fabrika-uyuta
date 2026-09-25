"""S1-04 AC2: every /api/v1/ operation answers 403 without the internal token."""

import pytest
from django.test import Client
from drf_spectacular.generators import SchemaGenerator

pytestmark = pytest.mark.django_db


def operations() -> list[tuple[str, str]]:
    schema = SchemaGenerator().get_schema(request=None, public=True)
    return [
        (method, path.replace("{slug}", "kitchens"))
        for path, item in schema["paths"].items()
        for method in item
    ]


@pytest.mark.parametrize(("method", "path"), operations())
@pytest.mark.parametrize("token", [None, "wrong-token", ""])
def test_ac2_missing_or_wrong_token_is_403(
    client: Client, method: str, path: str, token: str | None
) -> None:
    headers = {} if token is None else {"X-Internal-Token": token}
    response = getattr(client, method)(path, headers=headers, content_type="application/json")
    assert response.status_code == 403
    assert set(response.json()) == {"detail"}
