from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from apps.content import selectors
from apps.content.api.serializers import (
    CategoryDetailSerializer,
    HomeContentSerializer,
    SiteSettingsSerializer,
)
from apps.core.api import InternalAPIView
from apps.core.serializers import ErrorDetailSerializer


class SiteSettingsView(InternalAPIView):
    @extend_schema(responses={200: SiteSettingsSerializer, 403: ErrorDetailSerializer})
    def get(self, request: Request) -> Response:
        return Response(SiteSettingsSerializer(selectors.get_site_settings()).data)


class HomeView(InternalAPIView):
    @extend_schema(responses={200: HomeContentSerializer, 403: ErrorDetailSerializer})
    def get(self, request: Request) -> Response:
        return Response(HomeContentSerializer(selectors.get_home_content()).data)


class CategoryDetailView(InternalAPIView):
    @extend_schema(
        responses={
            200: CategoryDetailSerializer,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
        }
    )
    def get(self, request: Request, slug: str) -> Response:
        category = selectors.get_category_detail(slug)
        if category is None:
            raise NotFound
        return Response(CategoryDetailSerializer(category).data)
