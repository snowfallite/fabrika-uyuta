from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.api import InternalAPIView
from apps.leads.sheets.fake import FakeSheetsClient


class FakeSheetView(InternalAPIView):
    """E2E peeks at the fake sheet (tech.md, section 7); off unless ENABLE_TEST_ENDPOINTS."""

    @extend_schema(exclude=True)
    def get(self, request: Request) -> Response:
        if not settings.ENABLE_TEST_ENDPOINTS or settings.SHEETS_BACKEND != "fake":
            raise NotFound
        return Response({"rows": FakeSheetsClient(settings.SHEETS_FAKE_PATH).rows()})
