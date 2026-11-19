from pathlib import Path

from dotenv import load_dotenv

from apps.core.env import env_bool, env_int, env_list, env_str

BASE_DIR = Path(__file__).resolve().parent.parent

# Outside a container the root .env fills in missing variables; real env wins.
load_dotenv(BASE_DIR.parent / ".env", override=False)


def _path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (BASE_DIR / path).resolve()


APP_ENV = env_str("APP_ENV")
SECRET_KEY = env_str("DJANGO_SECRET_KEY")
DEBUG = env_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "")
DJANGO_ADMIN_PATH = env_str("DJANGO_ADMIN_PATH", "admin/")
INTERNAL_API_TOKEN = env_str("INTERNAL_API_TOKEN")
LEAD_THROTTLE_RATE = env_str("LEAD_THROTTLE_RATE", "5/hour")
CONSENT_VERSION = env_str("CONSENT_VERSION")
ENABLE_TEST_ENDPOINTS = env_bool("ENABLE_TEST_ENDPOINTS", False)
PUBLIC_SITE_URL = env_str("PUBLIC_SITE_URL", "").rstrip("/")

SHEETS_BACKEND = env_str("SHEETS_BACKEND", "fake")
SHEETS_FAKE_PATH = _path(env_str("SHEETS_FAKE_PATH", "./var/fake-sheet.jsonl"))
_sa_file = env_str("GOOGLE_SERVICE_ACCOUNT_FILE", "")
GOOGLE_SERVICE_ACCOUNT_FILE = _path(_sa_file) if _sa_file else None
GOOGLE_SPREADSHEET_ID = env_str("GOOGLE_SPREADSHEET_ID", "")
GOOGLE_WORKSHEET_TITLE = env_str("GOOGLE_WORKSHEET_TITLE", "Заявки")
SHEETS_TIMEZONE = env_str("SHEETS_TIMEZONE", "Europe/Moscow")
SHEETS_POLL_SECONDS = env_int("SHEETS_POLL_SECONDS", 5)
SHEETS_MAX_ATTEMPTS = env_int("SHEETS_MAX_ATTEMPTS", 12)

ALERT_EMAIL = env_str("ALERT_EMAIL", "")
# Recipients of lead notifications live in the admin: SiteSettings.notify_emails (tech.md, 24.1).
LEAD_NOTIFY_MAX_ATTEMPTS = env_int("LEAD_NOTIFY_MAX_ATTEMPTS", 6)
EMAIL_HOST = env_str("EMAIL_HOST", "")
EMAIL_PORT = env_int("EMAIL_PORT", 465)
EMAIL_HOST_USER = env_str("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env_str("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", True)
EMAIL_TIMEOUT = 10
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if EMAIL_HOST
    else "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = env_str("DEFAULT_FROM_EMAIL", "") or "webmaster@localhost"

MAX_BACKEND = env_str("MAX_BACKEND", "fake")
MAX_API_URL = env_str("MAX_API_URL", "https://platform-api2.max.ru").rstrip("/")
MAX_BOT_TOKEN = env_str("MAX_BOT_TOKEN", "")
# platform-api2.max.ru serves a Russian Trusted Root CA chain that certifi rejects, so the
# messenger client alone verifies against this bundle (tech.md, 25.2).
_max_ca = env_str("MAX_CA_BUNDLE", "")
MAX_CA_BUNDLE = str(_path(_max_ca)) if _max_ca else ""
MAX_FAKE_PATH = _path(env_str("MAX_FAKE_PATH", "./var/fake-max.jsonl"))
# The chat that receives new leads lives in the admin: SiteSettings.max_chat_id (tech.md, 25.1).
LEAD_MESSENGER_MAX_ATTEMPTS = env_int("LEAD_MESSENGER_MAX_ATTEMPTS", 6)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "axes",
    "apps.core",
    "apps.content",
    "apps.leads",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env_str("POSTGRES_DB"),
        "USER": env_str("POSTGRES_USER"),
        "PASSWORD": env_str("POSTGRES_PASSWORD"),
        "HOST": env_str("POSTGRES_HOST"),
        "PORT": env_int("POSTGRES_PORT", 5432),
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
        "OPTIONS": {"MAX_ENTRIES": 10000},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/django-static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = _path(env_str("MEDIA_ROOT", "./var/media"))
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Caddy terminates TLS and sets HSTS and the HTTPS redirect (tech.md, 16.4).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = APP_ENV in {"staging", "production"}
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
SILENCED_SYSTEM_CHECKS = ["security.W004", "security.W008"]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["apps.core.permissions.InternalTokenPermission"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_THROTTLE_RATES": {"leads": LEAD_THROTTLE_RATE},
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Фабрика Уюта: внутренний API",
    "VERSION": "1",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    # v15: no enum is left in the schema, so ENUM_NAME_OVERRIDES has nothing to pin.
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "InternalToken": {"type": "apiKey", "in": "header", "name": "X-Internal-Token"}
        }
    },
    "SECURITY": [{"InternalToken": []}],
}

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # hours
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
AXES_CLIENT_IP_CALLABLE = "apps.core.net.forwarded_client_ip"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"plain": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "plain"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
