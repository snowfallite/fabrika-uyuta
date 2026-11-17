"""/healthz: database and worker heartbeat (S1-04, S1-07 AC7)."""

import random
import time

import pytest
from django.core.cache import cache
from django.test import Client

from apps.leads.messenger.fake import FakeMessengerClient
from apps.leads.sheets.fake import FakeSheetsClient
from apps.leads.worker import HEARTBEAT_KEY, run_cycle

pytestmark = pytest.mark.django_db


def test_ac7_missing_heartbeat_is_degraded(client: Client) -> None:
    response = client.get("/healthz")
    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "checks": {"db": "ok", "worker": "stale"}}


def test_ac7_heartbeat_older_than_120s_is_degraded(client: Client) -> None:
    cache.set(HEARTBEAT_KEY, time.time() - 121)
    assert client.get("/healthz").status_code == 503


def test_ac7_ok_after_a_worker_cycle(client: Client) -> None:
    run_cycle(FakeSheetsClient(), FakeMessengerClient(), random.Random(1))  # noqa: S311
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
