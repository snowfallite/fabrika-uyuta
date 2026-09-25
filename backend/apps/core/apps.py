from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "apps.core"
    verbose_name = "Ядро"

    def ready(self) -> None:
        from apps.core import checks  # noqa: F401  registers deploy checks
