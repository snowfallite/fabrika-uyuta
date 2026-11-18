from typing import Final

from django.db import models


class ProductKind(models.TextChoices):
    KITCHENS = "kitchens", "Кухни под заказ"
    KITCHEN_TABLES = "kitchen-tables", "Кухонные столы"
    WARDROBES = "wardrobes", "Шкафы"
    SLIDING_WARDROBES = "sliding-wardrobes", "Шкафы-купе"
    OFFICE = "office", "Офисная мебель"
    OTHER = "other", "Другое"


# Seed of the category list; after the first run the owner edits it in the admin (tech.md, 15.2).
# The value doubles as the URL slug of the category page.
CATEGORY_SEED: Final[list[tuple[str, str]]] = [(v, label) for v, label in ProductKind.choices]


class SiteImageSlot(models.TextChoices):
    HERO = "hero", "Главный экран"
    ABOUT = "about", "О компании"
    MATERIAL_LDSP = "material_ldsp", "Материал ЛДСП"
    MATERIAL_MDF = "material_mdf", "Материал МДФ"


class SheetStatus(models.TextChoices):
    PENDING = "pending", "Ожидает отправки"
    SENT = "sent", "Отправлена"
    FAILED = "failed", "Ошибка отправки"


class NotifyStatus(models.TextChoices):
    PENDING = "pending", "Ожидает отправки"
    SENT = "sent", "Отправлено"
    FAILED = "failed", "Ошибка отправки"
    OFF = "off", "Не отправляется"
