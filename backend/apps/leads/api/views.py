import logging
import uuid

from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.api import ClientIPRateThrottle, InternalAPIView
from apps.core.serializers import ErrorDetailSerializer
from apps.leads.api.serializers import (
    LeadCreatedSerializer,
    LeadCreateErrorSerializer,
    LeadCreateSerializer,
)
from apps.leads.services.create_lead import create_lead

logger = logging.getLogger(__name__)


class LeadRateThrottle(ClientIPRateThrottle):
    scope = "leads"

    def get_rate(self) -> str:
        # Read at request time, so each environment and test sets its own limit.
        return str(settings.LEAD_THROTTLE_RATE)

    def allow_request(self, request: Request, view: APIView) -> bool:
        # Only POST exists here; other methods must still get their 405.
        return request.method != "POST" or super().allow_request(request, view)


class LeadCreateView(InternalAPIView):
    # Order (tech.md, section 7): token, throttle, honeypot, validation, save.
    throttle_classes = (LeadRateThrottle,)

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
        if isinstance(request.data, dict) and request.data.get("website"):
            logger.info("honeypot filled, lead dropped")
            return Response({"id": str(uuid.uuid4())}, status=status.HTTP_201_CREATED)
        serializer = LeadCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead = create_lead(serializer.validated_data, timezone.now())
        return Response({"id": str(lead.public_id)}, status=status.HTTP_201_CREATED)
