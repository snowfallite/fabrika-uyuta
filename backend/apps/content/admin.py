from typing import Any

from django import forms
from django.contrib import admin
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import SafeString

from apps.content.models import (
    Category,
    GalleryItem,
    ImageFieldsMixin,
    SiteImage,
    SiteSettings,
    SocialLink,
)
from apps.content.services.images import clear_image, ingest_image, validate_image_file


class ImageAdminForm(forms.ModelForm):
    def clean_image(self) -> Any:
        upload = self.cleaned_data.get("image")
        if isinstance(upload, UploadedFile):
            validate_image_file(upload)
        return upload


class ImageAdminMixin(admin.ModelAdmin):
    """Uploads go through the image pipeline (tech.md, section 9); no business logic here."""

    form = ImageAdminForm

    @admin.display(description="Превью")
    def image_preview(self, obj: ImageFieldsMixin) -> SafeString | str:
        variants = obj.image_variants or {}
        if not variants:
            return "—"
        smallest = variants[min(variants, key=int)]
        return format_html(
            '<img src="{}" alt="" style="height:64px;width:auto;border-radius:8px">',
            default_storage.url(smallest),
        )

    def save_model(
        self, request: HttpRequest, obj: ImageFieldsMixin, form: forms.ModelForm, change: bool
    ) -> None:
        upload = form.cleaned_data.get("image")
        if isinstance(upload, UploadedFile):
            ingest_image(obj, upload)
        elif upload is False:
            clear_image(obj)
        super().save_model(request, obj, form, change)


class ReferenceRowAdmin(admin.ModelAdmin):
    """Rows created by sync_reference_data: no adding, no deleting (tech.md, section 6)."""

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: object = None) -> bool:
        return False


@admin.register(Category)
class CategoryAdmin(ImageAdminMixin, ReferenceRowAdmin):
    """Five fixed categories (tech.md, S2-06): order and publication edit right in the list."""

    list_display = ["title", "image_preview", "slug", "position", "is_published"]
    list_display_links = ["title"]
    list_editable = ["position", "is_published"]
    readonly_fields = ["slug", "image_preview"]
    fieldsets = [
        (None, {"fields": ["slug", "title", "short_description", "description"]}),
        ("Обложка", {"fields": ["image", "image_preview", "alt"]}),
        ("SEO", {"fields": ["seo_title", "seo_description"]}),
        ("Показ", {"fields": ["position", "is_published"]}),
    ]


@admin.register(GalleryItem)
class GalleryItemAdmin(ImageAdminMixin):
    list_display = ["__str__", "image_preview", "category", "position", "is_published"]
    readonly_fields = ["image_preview"]


@admin.register(SiteImage)
class SiteImageAdmin(ImageAdminMixin, ReferenceRowAdmin):
    """Fixed photo slots of the home sections (tech.md, S1-09)."""

    list_display = ["__str__", "image_preview", "updated_at"]
    fields = ["slot", "image", "image_preview", "alt"]
    readonly_fields = ["slot", "image_preview"]


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 0


@admin.register(SiteSettings)
class SiteSettingsAdmin(ReferenceRowAdmin):
    inlines = [SocialLinkInline]
