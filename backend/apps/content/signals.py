"""File cleanup only (tech.md, section 5): a deleted record takes its image folder along."""

from typing import Any

from django.db.models.signals import post_delete
from django.dispatch import receiver

from apps.content.models import Category, GalleryItem, ImageFieldsMixin, SiteImage
from apps.content.services.images import schedule_folder_removal


@receiver(post_delete, sender=Category)
@receiver(post_delete, sender=GalleryItem)
@receiver(post_delete, sender=SiteImage)
def remove_image_folder(sender: type, instance: ImageFieldsMixin, **kwargs: Any) -> None:
    if instance.image:
        schedule_folder_removal(instance.image.name)
