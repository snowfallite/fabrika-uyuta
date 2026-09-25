from django.db import models


class ProductKind(models.TextChoices):
    KITCHENS = "kitchens", "Кухни под заказ"
    KITCHEN_TABLES = "kitchen-tables", "Кухонные столы"
    WARDROBES = "wardrobes", "Шкафы"
    SLIDING_WARDROBES = "sliding-wardrobes", "Шкафы-купе"
    OFFICE = "office", "Офисная мебель"
    OTHER = "other", "Другое"


# Every kind except OTHER has a category page; the value doubles as the URL slug.
CATEGORY_SLUG_CHOICES = [(v, label) for v, label in ProductKind.choices if v != ProductKind.OTHER]


class SiteImageSlot(models.TextChoices):
    HERO = "hero", "Главный экран"
    ABOUT = "about", "О компании"
    MATERIAL_LDSP = "material_ldsp", "Материал ЛДСП"
    MATERIAL_MDF = "material_mdf", "Материал МДФ"


class SheetStatus(models.TextChoices):
    PENDING = "pending", "Ожидает отправки"
    SENT = "sent", "Отправлена"
    FAILED = "failed", "Ошибка отправки"
