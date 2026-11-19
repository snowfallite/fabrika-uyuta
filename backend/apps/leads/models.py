import uuid

from django.db import models
from django.utils import timezone

from apps.core.enums import NotifyStatus, SheetStatus


class Lead(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField("ФИО", max_length=120)
    phone = models.CharField("Телефон", max_length=16)  # E.164
    # Category.slug; the set of kinds is editable data since v15, so no choices here.
    product = models.CharField("Что заказать", max_length=32)
    # Title of that category when the lead arrived; empty on leads made before v15.
    product_label = models.CharField("Название вида", max_length=120, blank=True)
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

    # Second outbox: the email to the managers (tech.md, 24). Leads enter the queue through
    # create_lead, so rows that predate the feature stay out of it.
    notify_status = models.CharField(
        "Уведомление", max_length=16, choices=NotifyStatus.choices, default=NotifyStatus.OFF
    )
    notify_attempts = models.PositiveSmallIntegerField("Попытки уведомления", default=0)
    notify_next_attempt_at = models.DateTimeField("Следующее уведомление", default=timezone.now)
    # SMTP code and error class only, never PII or recipient addresses.
    notify_last_error = models.CharField("Ошибка уведомления", max_length=500, blank=True)
    notify_sent_at = models.DateTimeField("Уведомление отправлено", null=True, blank=True)

    # Third outbox: the message to the MAX group chat (tech.md, 25). Same rule as the email:
    # create_lead queues new leads, rows that predate the feature stay out.
    max_status = models.CharField(
        "MAX", max_length=16, choices=NotifyStatus.choices, default=NotifyStatus.OFF
    )
    max_attempts = models.PositiveSmallIntegerField("Попытки отправки в MAX", default=0)
    max_next_attempt_at = models.DateTimeField("Следующая отправка в MAX", default=timezone.now)
    # HTTP status or MAX error code plus the error class, never PII and never the token.
    max_last_error = models.CharField("Ошибка отправки в MAX", max_length=500, blank=True)
    max_sent_at = models.DateTimeField("Отправлена в MAX", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            ("retry_sheet_sync", "Может повторить отправку в таблицу"),
            ("retry_notify", "Может повторить уведомление"),
            ("retry_max", "Может повторить отправку в MAX"),
        ]
        indexes = [
            models.Index(
                fields=["sheet_next_attempt_at"],
                name="lead_sheet_due_idx",
                condition=models.Q(sheet_status="pending"),
            ),
            models.Index(
                fields=["notify_next_attempt_at"],
                name="lead_notify_due_idx",
                condition=models.Q(notify_status="pending"),
            ),
            models.Index(
                fields=["max_next_attempt_at"],
                name="lead_max_due_idx",
                condition=models.Q(max_status="pending"),
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
            models.CheckConstraint(
                condition=~models.Q(notify_status="sent") | models.Q(notify_sent_at__isnull=False),
                name="lead_notified_has_sent_at",
            ),
            models.CheckConstraint(
                condition=~models.Q(max_status="sent") | models.Q(max_sent_at__isnull=False),
                name="lead_max_sent_has_sent_at",
            ),
        ]
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self) -> str:
        return f"Заявка {self.public_id}"
