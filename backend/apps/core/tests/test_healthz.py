import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_healthz_ok_with_database(client: Client) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
