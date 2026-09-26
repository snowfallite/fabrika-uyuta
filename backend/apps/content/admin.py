from __future__ import annotations

from typing import Any

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import URLPattern, path
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
from apps.content.services.batch_upload import MAX_FILES, upload_gallery_batch
from apps.content.services.images import clear_image, ingest_image, validate_image_file
from apps.core.phone import normalize_phone


class ImageAdminForm(forms.ModelForm):
    def clean_image(self) -> Any:
        upload = self.cleaned_data.get("image")
        if isinstance(upload, UploadedFile):
            validate_image_file(upload)
        return upload


def preview_html(obj: ImageFieldsMixin) -> SafeString | str:
    variants = obj.image_variants or {}
    if not variants:
        return "—"
    smallest = variants[min(variants, key=int)]
    return format_html(
        '<img src="{}" alt="" style="height:64px;width:auto;border-radius:8px">',
        default_storage.url(smallest),
    )


class ImageAdminMixin(admin.ModelAdmin):
    """Uploads go through the image pipeline (tech.md, section 9); no business logic here."""

    form = ImageAdminForm

    @admin.display(description="Превью")
    def image_preview(self, obj: ImageFieldsMixin) -> SafeString | str:
        return preview_html(obj)

    def save_model(
        self, request: HttpRequest, obj: ImageFieldsMixin, form: forms.ModelForm, change: bool
    ) -> None:
        upload = form.cleaned_data.get("image")
        if isinstance(upload, UploadedFile):
            ingest_image(obj, upload)
        elif upload is False:
            clear_image(obj)
        super().save_model(request, obj, form, change)


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault(
            "widget", MultipleFileInput(attrs={"accept": "image/jpeg,image/png,image/webp"})
        )
        super().__init__(**kwargs)

    def clean(self, data: Any, initial: Any = None) -> list[UploadedFile]:
        files = data if isinstance(data, list | tuple) else [data] if data else []
        return [super(MultipleFileField, self).clean(file, initial) for file in files]


class GalleryUploadForm(forms.Form):
    photos = MultipleFileField(label="Фото", required=False)


class ReferenceRowAdmin(admin.ModelAdmin):
    """Rows created by sync_reference_data: no adding, no deleting (tech.md, section 6)."""

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: object = None) -> bool:
        return False


class GalleryItemInline(admin.TabularInline):
    """Order and flags of a category's works; photos go through the gallery admin."""

    model = GalleryItem
    extra = 0
    fields = ["preview", "title", "position", "is_published", "is_featured"]
    readonly_fields = ["preview"]
    show_change_link = True

    @admin.display(description="Превью")
    def preview(self, obj: GalleryItem) -> SafeString | str:
        return preview_html(obj)

    def has_add_permission(self, request: HttpRequest, obj: object = None) -> bool:
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
    inlines = [GalleryItemInline]

    def get_urls(self) -> list[URLPattern]:
        upload = path(
            "<int:pk>/upload/",
            self.admin_site.admin_view(self.upload_view),
            name="content_category_upload",
        )
        return [upload, *super().get_urls()]

    def upload_view(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Up to 20 photos into this category's gallery (tech.md, S2-09)."""
        category = get_object_or_404(Category, pk=pk)
        if not self.has_change_permission(request, category):
            raise PermissionDenied
        form = GalleryUploadForm(request.POST or None, request.FILES or None)
        if request.method == "POST" and form.is_valid():
            try:
                created = upload_gallery_batch(category, form.cleaned_data["photos"])
            except ValidationError as exc:
                form.add_error("photos", exc)
            else:
                self.message_user(request, f"Загружено фото: {len(created)}.", messages.SUCCESS)
                return redirect("admin:content_category_change", category.pk)
        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "category": category,
            "form": form,
            "max_files": MAX_FILES,
            "title": f"Загрузить фото: {category}",
        }
        return TemplateResponse(request, "admin/content/category/upload.html", context)


@admin.register(GalleryItem)
class GalleryItemAdmin(ImageAdminMixin):
    list_display = [
        "__str__",
        "image_preview",
        "category",
        "position",
        "is_published",
        "is_featured",
    ]
    list_display_links = ["__str__"]
    list_editable = ["position", "is_published", "is_featured"]
    list_filter = ["category", "is_published", "is_featured"]
    list_select_related = ["category"]
    readonly_fields = ["image_preview"]
    fields = [
        "category",
        "image",
        "image_preview",
        "alt",
        "title",
        "caption",
        "position",
        "is_published",
        "is_featured",
    ]


@admin.register(SiteImage)
class SiteImageAdmin(ImageAdminMixin, ReferenceRowAdmin):
    """Fixed photo slots of the home sections (tech.md, S1-09)."""

    list_display = ["__str__", "image_preview", "updated_at"]
    fields = ["slot", "image", "image_preview", "alt"]
    readonly_fields = ["slot", "image_preview"]


# Links typed without a scheme get https, the Django 6 default.
HTTPS_URLS: dict[type[models.Field[Any, Any]], dict[str, Any]] = {
    models.URLField: {"assume_scheme": "https"}
}


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 0
    formfield_overrides = HTTPS_URLS


class SiteSettingsForm(forms.ModelForm):
    # Wider than the E.164 column: people type "+7 (817) 200-00-00".
    phone = forms.CharField(label="Телефон", max_length=32, required=False)
    map_url = forms.URLField(
        label="Ссылка на карту", max_length=200, required=False, assume_scheme="https"
    )

    class Meta:
        model = SiteSettings
        fields = ["phone", "email", "address", "work_hours", "map_url"]

    def clean_phone(self) -> str:
        raw = self.cleaned_data["phone"]
        if not raw:
            return ""
        phone = normalize_phone(raw)
        if phone is None:
            raise ValidationError("Проверьте номер телефона")
        return phone


@admin.register(SiteSettings)
class SiteSettingsAdmin(ReferenceRowAdmin):
    """One contacts row (tech.md, S2-10): the menu item opens its form directly."""

    form = SiteSettingsForm
    inlines = [SocialLinkInline]
    formfield_overrides = HTTPS_URLS

    def changelist_view(self, request: HttpRequest, extra_context: Any = None) -> HttpResponse:
        return redirect("admin:content_sitesettings_change", 1)
