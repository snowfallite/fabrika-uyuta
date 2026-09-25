"""Demo content for dev, e2e and staging (tech.md, 15.3). Fictitious data only."""

import uuid
from io import BytesIO
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont, ImageOps

from apps.content.models import Category, GalleryItem, ImageFieldsMixin, SiteImage, SiteSettings
from apps.content.services.images import clear_image, ingest_image
from apps.core.enums import ProductKind, SheetStatus, SiteImageSlot
from apps.leads.models import Lead

ALLOWED_ENVS = {"dev", "e2e", "staging"}
FIXTURES = Path(settings.BASE_DIR) / "fixtures" / "demo"

# Template palette (tech.md, section 11) for generated pictures.
PALETTES = [
    ((239, 235, 230), (103, 82, 66)),
    ((194, 180, 142), (103, 82, 66)),
    ((243, 240, 237), (160, 138, 106)),
    ((175, 120, 106), (75, 60, 48)),
]

SLOTS = {
    SiteImageSlot.HERO: ("hero", (1600, 2000)),
    SiteImageSlot.ABOUT: ("about", (1400, 1750)),
    SiteImageSlot.MATERIAL_LDSP: ("material_ldsp", (1200, 900)),
    SiteImageSlot.MATERIAL_MDF: ("material_mdf", (1200, 900)),
}

CATEGORY_TEXTS = {
    "kitchens": "Кухонные гарнитуры по индивидуальным размерам.",
    "kitchen-tables": "Обеденные и рабочие столы под вашу кухню.",
    "wardrobes": "Распашные шкафы и гардеробные под ваши размеры.",
    "sliding-wardrobes": "Системы хранения под ваши габариты.",
    "office": "Столы, стеллажи и стойки для рабочих пространств.",
}
DEMO_DESCRIPTION = (
    "Демо-описание категории. Проектируем мебель под размеры помещения и согласуем материалы.\n\n"
    "Второй абзац демо-описания: замер, проект, производство и монтаж."
)

# (title, category slug, featured)
GALLERY = [
    ("Кухня «Тёплый орех»", "kitchens", True),
    ("Шкаф-купе в прихожую", "sliding-wardrobes", True),
    ("Рабочее место для офиса", "office", True),
    ("Кухонный стол", "kitchen-tables", True),
    ("Угловая кухня", "kitchens", False),
    ("Гардеробная", "wardrobes", False),
    ("Светлая кухня с островом", "kitchens", False),
    ("Шкаф в спальню", "wardrobes", False),
    ("Шкаф-купе с зеркалом", "sliding-wardrobes", False),
    ("Раздвижной стол", "kitchen-tables", False),
    ("Стеллаж для офиса", "office", False),
    ("Кухня в стиле лофт", "kitchens", False),
]

CONTACTS = {
    "phone": "+78172000000",
    "email": "info@example.ru",
    "address": "Вологда",
    "work_hours": "Пн–Пт, 9:00–18:00",
    "map_url": "https://yandex.ru/maps/?text=%D0%92%D0%BE%D0%BB%D0%BE%D0%B3%D0%B4%D0%B0",
}

# Fixed ids keep the demo leads idempotent, the fake sheet included.
LEADS = [
    (uuid.UUID("8f1d9c1e-0000-4000-8000-000000000001"), SheetStatus.PENDING),
    (uuid.UUID("8f1d9c1e-0000-4000-8000-000000000002"), SheetStatus.SENT),
    (uuid.UUID("8f1d9c1e-0000-4000-8000-000000000003"), SheetStatus.FAILED),
]


class Command(BaseCommand):
    help = "Fill demo content: slots, category covers, gallery, contacts, leads."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--reset", action="store_true", help="recreate demo data")

    def handle(self, *args: Any, reset: bool = False, **options: Any) -> None:
        if settings.APP_ENV not in ALLOWED_ENVS:
            raise CommandError(f"seed_demo runs only in {sorted(ALLOWED_ENVS)}")
        with transaction.atomic():
            if reset:
                self._reset()
            self._slots()
            self._categories()
            self._gallery()
            self._contacts()
            self._leads()
        self.stdout.write("Demo data is in place.")

    def _reset(self) -> None:
        GalleryItem.objects.filter(title__in=[title for title, _, _ in GALLERY]).delete()
        Lead.objects.filter(public_id__in=[lead_id for lead_id, _ in LEADS]).delete()
        for image in [*SiteImage.objects.all(), *Category.objects.all()]:
            if image.image:
                clear_image(image)
                image.save()
        SiteSettings.objects.filter(id=1).update(**CONTACTS)
        SiteSettings.objects.get(id=1).social_links.all().delete()

    def _slots(self) -> None:
        for slot, (key, size) in SLOTS.items():
            image, _ = SiteImage.objects.get_or_create(slot=slot)
            if not image.image:
                _attach(image, key, size)
                image.save()

    def _categories(self) -> None:
        for category in Category.objects.all():
            category.short_description = category.short_description or CATEGORY_TEXTS.get(
                category.slug, ""
            )
            category.description = category.description or DEMO_DESCRIPTION
            if not category.image:
                _attach(category, f"category-{category.slug}", (1200, 1500))
            category.save()

    def _gallery(self) -> None:
        categories = {category.slug: category for category in Category.objects.all()}
        for position, (title, slug, featured) in enumerate(GALLERY, start=1):
            if GalleryItem.objects.filter(title=title).exists():
                continue
            item = GalleryItem(
                category=categories[slug],
                title=title,
                caption="Демо-работа",
                position=position,
                is_featured=featured,
            )
            size = (1200, 900) if position % 2 else (900, 1200)
            _attach(item, f"gallery-{position:02d}", size)
            item.save()

    def _contacts(self) -> None:
        contacts, _ = SiteSettings.objects.get_or_create(id=1)
        for field, value in CONTACTS.items():
            if not getattr(contacts, field):
                setattr(contacts, field, value)
        contacts.save()
        if not contacts.social_links.exists():
            contacts.social_links.create(label="ВКонтакте", url="https://vk.com/", position=0)

    def _leads(self) -> None:
        now = timezone.now()
        for number, (lead_id, status) in enumerate(LEADS, start=1):
            Lead.objects.get_or_create(
                public_id=lead_id,
                defaults={
                    "name": f"Демо Клиент {number}",
                    "phone": f"+7999000000{number}",
                    "product": ProductKind.KITCHENS,
                    "dimensions": "Стена 3,2 м, высота 2,6 м",
                    "comment": "Демо-заявка",
                    "source_url": "/",
                    "consent_version": settings.CONSENT_VERSION,
                    "consent_at": now,
                    "sheet_status": status,
                    "sheet_synced_at": now if status == SheetStatus.SENT else None,
                    "sheet_attempts": settings.SHEETS_MAX_ATTEMPTS
                    if status == SheetStatus.FAILED
                    else 0,
                    "sheet_last_error": "403 SheetsPermanentError"
                    if status == SheetStatus.FAILED
                    else "",
                },
            )


def _attach(instance: ImageFieldsMixin, key: str, size: tuple[int, int]) -> None:
    """A real photo from fixtures/demo/<key>.jpg wins over a generated picture."""
    photo = FIXTURES / f"{key}.jpg"
    data = photo.read_bytes() if photo.exists() else _generate(key, size)
    ingest_image(instance, ContentFile(data, name=f"{key}.jpg"))


def _generate(key: str, size: tuple[int, int]) -> bytes:
    """Gradient in template colors with a caption naming the picture."""
    light, dark = PALETTES[sum(key.encode()) % len(PALETTES)]
    image = ImageOps.colorize(Image.linear_gradient("L").resize(size), black=light, white=dark)
    font = ImageFont.load_default(size=max(24, size[0] // 30))
    # The bundled font has no Cyrillic, so the caption stays ASCII.
    label = f"demo | {key.replace('_', ' ').replace('-', ' ')}"
    # Top left in the dark tone: card titles on the site sit at the bottom.
    ImageDraw.Draw(image).text((size[0] // 20, size[1] // 20), label, fill=dark, font=font)
    buffer = BytesIO()
    image.save(buffer, "JPEG", quality=85)
    return buffer.getvalue()
