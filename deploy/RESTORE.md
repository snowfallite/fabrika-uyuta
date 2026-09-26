# Восстановление из бэкапа

Бэкап делает `deploy/backup.sh <staging|production>` каждую ночь (cron в шапке скрипта). Файлы лежат в `/opt/fabrika/backups/<env>/` 14 дней, копия уходит в S3-совместимое хранилище, если есть `/opt/fabrika/backup.env`:

- `db-<время>.dump`: `pg_dump -Fc` базы;
- `media-<время>.tar.gz`: содержимое тома `fabrika-<env>_media`.

Шаги ниже проверены на чистых контейнерах: заявки, контент и файлы media возвращаются полностью.

## 1. Взять бэкап

Локальная копия: самые свежие `db-*.dump` и `media-*.tar.gz` в `/opt/fabrika/backups/production/`.

Из хранилища (переменные из `/opt/fabrika/backup.env`):

```sh
. /opt/fabrika/backup.env
mkdir -p /opt/fabrika/restore
docker run --rm -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION \
  -v /opt/fabrika/restore:/restore amazon/aws-cli --endpoint-url "$S3_ENDPOINT" \
  s3 cp "s3://$S3_BUCKET/production/" /restore/ --recursive --exclude "*" \
  --include "db-<время>.dump" --include "media-<время>.tar.gz"
```

## 2. Поднять пустой стек (только для нового VPS)

1. Docker, `docker login ghcr.io`, папка `deploy/` в `/opt/fabrika/app/deploy/`.
2. `/opt/fabrika/production/.env` и `/opt/fabrika/production/google-sa.json` из хранилища секретов.
3. Один раз: `docker network create edge`, `docker volume create fabrika-staging_media`, `docker volume create fabrika-production_media`, edge Caddy: `docker compose -f /opt/fabrika/app/deploy/edge/compose.yml up -d`.
4. `GHCR_OWNER=<owner> /opt/fabrika/app/deploy/deploy.sh production <тег>`: создаёт пустую базу и тома.

## 3. Восстановить

```sh
STACK=fabrika-production
BACKUP=/opt/fabrika/backups/production   # или /opt/fabrika/restore
STAMP=<время из имени файла>

# Приложение не пишет в базу, пока идёт восстановление.
docker stop "$STACK-backend-1" "$STACK-worker-1" "$STACK-frontend-1"

docker exec -i "$STACK-db-1" sh -c \
  'pg_restore --clean --if-exists --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  < "$BACKUP/db-$STAMP.dump"

docker run --rm -v "${STACK}_media:/media" -v "$BACKUP:/backup:ro" alpine:3 \
  sh -c "rm -rf /media/* && tar -xzf /backup/media-$STAMP.tar.gz -C /media"

GHCR_OWNER=<owner> /opt/fabrika/app/deploy/deploy.sh production <тег>
```

`deploy.sh` снова прогонит release-шаг (`migrate` дотянет схему, если бэкап старше кода) и дождётся healthy.

## 4. Проверить

1. `deploy/smoke.sh https://<domain>` проходит.
2. В админке список заявок совпадает с ожидаемым, последние заявки на месте.
3. Фото на главной и в галерее открываются.
4. Заявки со статусом «Ожидает отправки» уходят в таблицу: воркер допишет недостающие строки, дублей не будет (проверка ID в колонке A).

## Мониторинг

Внешний сервис (например, Uptime Kuma или любой сервис проверки доступности) опрашивает `https://<domain>/healthz` раз в минуту и шлёт алерт, если ответ не 200 дольше 5 минут. `/healthz` фронтенда отвечает 503, когда недоступен бэкенд, база или воркер перестал писать heartbeat.
