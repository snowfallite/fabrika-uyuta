import time

from django.core.cache import cache
from django.db import connection
from django.http import HttpRequest, JsonResponse

from apps.leads.worker import HEARTBEAT_KEY

HEARTBEAT_MAX_AGE = 120  # seconds


def _db_ok() -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return False
    return True


def _worker_ok() -> bool:
    try:
        beat = cache.get(HEARTBEAT_KEY)
    except Exception:
        return False
    return beat is not None and time.time() - float(beat) <= HEARTBEAT_MAX_AGE


def healthz(request: HttpRequest) -> JsonResponse:
    """Liveness for deploy and monitoring; no token, outside the API schema."""
    checks = {
        "db": "ok" if _db_ok() else "error",
        "worker": "ok" if _worker_ok() else "stale",
    }
    if all(value == "ok" for value in checks.values()):
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "degraded", "checks": checks}, status=503)
