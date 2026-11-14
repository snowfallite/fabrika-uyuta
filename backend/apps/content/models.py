from django.db import models

from apps.core.enums import CATEGORY_SLUG_CHOICES, SiteImageSlot

ALT_HELP = "Что на фото: для незрячих и поисковиков"


class ImageFieldsMixin(models.Model):
    # Written only by services.images.ingest_image.
    image = models.ImageField("Фото", upload_to="content/", max_length=255)
    image_width = models.PositiveIntegerField(null=True, editable=False)
    image_height = models.PositiveIntegerField(null=True, editable=False)
    # {"640": "content/<uuid>/w640.webp"}
    image_variants = models.JSONField(default=dict, editable=False)
    image_color = models.CharField(max_length=7, blank=True, editable=False)  # "#a07850"
    alt = models.CharField("Описание фото (alt)", max_length=200, blank=True, help_text=ALT_HELP)

    class Meta:
        abstract = True


class Category(ImageFieldsMixin):
    image = models.ImageField("Обложка", upload_to="content/", max_length=255, blank=True)
    slug = models.CharField(max_length=32, unique=True, choices=CATEGORY_SLUG_CHOICES)
    title = models.CharField("Название", max_length=120)
    short_description = models.CharField("Кратко", max_length=300, blank=True)
    # Plain text, paragraphs split by a blank line.
    description = models.TextField("Описание", blank=True)
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    position = models.PositiveSmallIntegerField("Порядок", default=0)
    is_published = models.BooleanField("Опубликовано", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.title


class GalleryItem(ImageFieldsMixin):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="gallery_items")
    title = models.CharField("Название", max_length=120, blank=True)
    caption = models.CharField("Подпись", max_length=300, blank=True)
    position = models.PositiveIntegerField("Порядок", default=0)
    is_published = models.BooleanField("Опубликовано", default=True)
    is_featured = models.BooleanField("На главной", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "-created_at"]
        indexes = [
            models.Index(
                fields=["category", "is_published", "position"], name="gallery_cat_pub_pos_idx"
            ),
            models.Index(
                fields=["is_featured", "is_published", "position"], name="gallery_featured_idx"
            ),
        ]
        verbose_name = "Работа"
        verbose_name_plural = "Галерея работ"

    def __str__(self) -> str:
        return self.title or f"Работа #{self.pk}"


class SiteImage(ImageFieldsMixin):
    # Empty slot allowed.
    image = models.ImageField("Фото", upload_to="content/", max_length=255, blank=True)
    slot = models.CharField(max_length=32, unique=True, choices=SiteImageSlot.choices)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Фото сайта"
        verbose_name_plural = "Фото сайта"

    def __str__(self) -> str:
        return SiteImageSlot(self.slot).label


class SiteSettings(models.Model):
    phone = models.CharField("Телефон", max_length=16, blank=True)  # E.164, normalized on save
    # MAX has no profile URL keyed by number, so the contact is the number itself (tech.md, v8).
    max_phone = models.CharField("Номер в MAX", max_length=16, blank=True)  # E.164
    email = models.EmailField(blank=True)
    address = models.CharField("Адрес", max_length=300, blank=True)
    work_hours = models.CharField("Часы работы", max_length=120, blank=True)
    map_url = models.URLField("Ссылка на карту", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(id=1), name="site_settings_singleton")
        ]
        verbose_name = "Контакты"
        verbose_name_plural = "Контакты"

    def __str__(self) -> str:
        return "Контакты"


class SocialLink(models.Model):
    settings = models.ForeignKey(
        SiteSettings, on_delete=models.CASCADE, related_name="social_links"
    )
    label = models.CharField(max_length=40)
    url = models.URLField()
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Соцсеть"
        verbose_name_plural = "Соцсети"

    def __str__(self) -> str:
        return self.label
