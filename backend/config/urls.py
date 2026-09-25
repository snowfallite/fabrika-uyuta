from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from apps.core.views import healthz

admin.site.site_header = "Фабрика Уюта"
admin.site.site_title = "Фабрика Уюта"
admin.site.index_title = "Управление сайтом"

urlpatterns = [
    path(settings.DJANGO_ADMIN_PATH, admin.site.urls),
    path("healthz", healthz),
    path("api/v1/", include("apps.content.api.urls")),
    path("api/v1/", include("apps.leads.api.urls")),
]
