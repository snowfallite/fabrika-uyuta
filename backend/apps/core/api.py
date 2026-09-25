"""Internal API plumbing: no-store responses and client IP throttling."""

from typing import Any

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView

from apps.core.net import api_client_ip
from apps.core.permissions import InternalTokenPermission


class InternalAPIView(APIView):
    authentication_classes = ()
    permission_classes = (InternalTokenPermission,)

    def finalize_response(
        self, request: Request, response: Response, *args: Any, **kwargs: Any
    ) -> Response:
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "no-store"
        return response


class ClientIPRateThrottle(SimpleRateThrottle):
    """Keys on X-Client-IP from SvelteKit, REMOTE_ADDR as a fallback."""

    def get_cache_key(self, request: Request, view: APIView) -> str:
        return self.cache_format % {"scope": self.scope, "ident": api_client_ip(request.META)}
