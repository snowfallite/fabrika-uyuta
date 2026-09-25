from __future__ import annotations

import hmac
from typing import TYPE_CHECKING

from django.conf import settings
from rest_framework.permissions import BasePermission

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView


class InternalTokenPermission(BasePermission):
    """Only SvelteKit knows INTERNAL_API_TOKEN; anything else gets 403 (tech.md, section 7).

    Lives apart from apps.core.api: DRF imports it while loading rest_framework.views.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        token = request.headers.get("X-Internal-Token", "")
        return hmac.compare_digest(token.encode(), settings.INTERNAL_API_TOKEN.encode())
