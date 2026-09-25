import uuid

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.api import InternalAPIView
from apps.core.serializers import ErrorDetailSerializer
from apps.leads.api.serializers import (
    LeadCreatedSerializer,
    LeadCreateErrorSerializer,
    LeadCreateSerializer,
)


class LeadCreateView(InternalAPIView):
    @extend_schema(
        request=LeadCreateSerializer,
        responses={
            201: LeadCreatedSerializer,
            400: LeadCreateErrorSerializer,
            403: ErrorDetailSerializer,
            429: ErrorDetailSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        serializer = LeadCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Stub until S2-01: validates, stores nothing.
        return Response({"id": str(uuid.uuid4())}, status=status.HTTP_201_CREATED)
