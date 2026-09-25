"""Schemathesis: every operation, no 5xx, responses match contracts/openapi.yaml."""

from collections.abc import Iterator
from pathlib import Path

import pytest
import schemathesis
from django.conf import settings
from django.core.signals import request_finished, request_started
from django.db import close_old_connections
from schemathesis.specs.openapi.checks import positive_data_acceptance

from config.wsgi import application

schema = schemathesis.openapi.from_path(
    Path(settings.BASE_DIR).parent / "contracts" / "openapi.yaml"
)
# Requests go straight into the WSGI app, extra check requests included.
schema.app = application
schema.config.update(base_url="http://localhost")


@pytest.fixture(autouse=True)
def keep_test_connection() -> Iterator[None]:
    """Like Django's test client: requests must not close the connection holding the test
    transaction."""
    request_started.disconnect(close_old_connections)
    request_finished.disconnect(close_old_connections)
    yield
    request_started.connect(close_old_connections)
    request_finished.connect(close_old_connections)


@pytest.mark.django_db
@schema.parametrize()
def test_api_matches_schema(case: schemathesis.Case) -> None:
    case.call_and_validate(
        headers={"X-Internal-Token": settings.INTERNAL_API_TOKEN},
        # Business rules reject schema-valid input (a phone that is just digits, a name
        # without letters), so valid-by-schema does not mean accepted.
        excluded_checks=[positive_data_acceptance],  # type: ignore[list-item]  # a check object
    )
