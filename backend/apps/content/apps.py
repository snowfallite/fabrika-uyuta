from django.apps import AppConfig


class ContentConfig(AppConfig):
    name = "apps.content"
    verbose_name = "Контент"

    def ready(self) -> None:
        from apps.content import signals  # noqa: F401  connects file cleanup
