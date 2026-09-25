import uuid

from django.db import models
from django.utils import timezone

from apps.core.enums import ProductKind, SheetStatus


class Lead(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField("ФИО", max_length=120)
    phone = models.CharField("Телефон", max_length=16)  # E.164
    product = models.CharField("Что заказать", max_length=32, choices=ProductKind.choices)
    dimensions = models.CharField("Размеры", max_length=300, blank=True)
    comment = models.TextField("Комментарий", blank=True)  # the API caps it at 2000
    source_url = models.CharField("Источник", max_length=500, blank=True)  # path + query, no host
    consent_version = models.CharField("Версия согласия", max_length=32)
    consent_at = models.DateTimeField("Время согласия")
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    sheet_status = models.CharField(
        "Статус отправки", max_length=16, choices=SheetStatus.choices, default=SheetStatus.PENDING
    )
    sheet_attempts = models.PositiveSmallIntegerField("Попытки", default=0)
    sheet_next_attempt_at = models.DateTimeField("Следующая попытка", default=timezone.now)
    # Status and error class only, never PII.
    sheet_last_error = models.CharField("Последняя ошибка", max_length=500, blank=True)
    sheet_synced_at = models.DateTimeField("Отправлена в таблицу", null=True, blank=True)
    sheet_alerted_at = models.DateTimeField("Алерт отправлен", null=True, blank=True)  # 8.4

    class Meta:
        ordering = ["-created_at"]
        permissions = [("retry_sheet_sync", "Может повторить отправку в таблицу")]
        indexes = [
            models.Index(
                fields=["sheet_next_attempt_at"],
                name="lead_sheet_due_idx",
                condition=models.Q(sheet_status="pending"),
            ),
            models.Index(fields=["created_at"], name="lead_created_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(phone__regex=r"^\+[1-9][0-9]{7,14}$"),
                name="lead_phone_e164",
            ),
            models.CheckConstraint(
                condition=~models.Q(sheet_status="sent") | models.Q(sheet_synced_at__isnull=False),
                name="lead_sent_has_synced_at",
            ),
        ]
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self) -> str:
        return f"Заявка {self.public_id}"
