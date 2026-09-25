from django.db import connection
from django.http import HttpRequest, JsonResponse


def _db_ok() -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return False
    return True


def healthz(request: HttpRequest) -> JsonResponse:
    """Liveness for deploy and monitoring; no token, outside the API schema."""
    checks = {"db": "ok" if _db_ok() else "error"}
    if all(value == "ok" for value in checks.values()):
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "degraded", "checks": checks}, status=503)
