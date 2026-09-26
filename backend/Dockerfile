# Build context: repository root (tech.md, 16.5). One image, three roles: web, worker, release.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv

WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY backend/ ./
# Settings need their variables to import; these values exist only in this build step.
RUN APP_ENV=dev DJANGO_SECRET_KEY=build INTERNAL_API_TOKEN=build CONSENT_VERSION=build \
    POSTGRES_DB=build POSTGRES_USER=build POSTGRES_PASSWORD=build POSTGRES_HOST=build \
    python manage.py collectstatic --noinput

RUN useradd --system --uid 10001 --home-dir /app app \
    && mkdir -p /data/media \
    && chown -R app /data
USER app

EXPOSE 8000
# No control socket: nothing uses it, and /app is read-only for the app user.
CMD ["gunicorn", "config.wsgi", "-k", "gthread", "-w", "2", "--threads", "4", "-t", "120", "-b", "0.0.0.0:8000", "--no-control-socket"]
