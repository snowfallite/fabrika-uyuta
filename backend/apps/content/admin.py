from django.contrib import admin
from django.http import HttpRequest

from apps.content.models import Category, GalleryItem, SiteImage, SiteSettings, SocialLink


class ReferenceRowAdmin(admin.ModelAdmin):
    """Rows created by sync_reference_data: no adding, no deleting (tech.md, section 6)."""

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: object = None) -> bool:
        return False


@admin.register(Category)
class CategoryAdmin(ReferenceRowAdmin):
    list_display = ["title", "slug", "position", "is_published"]


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ["__str__", "category", "position", "is_published", "is_featured"]


@admin.register(SiteImage)
class SiteImageAdmin(ReferenceRowAdmin):
    list_display = ["__str__", "updated_at"]


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 0


@admin.register(SiteSettings)
class SiteSettingsAdmin(ReferenceRowAdmin):
    inlines = [SocialLinkInline]
