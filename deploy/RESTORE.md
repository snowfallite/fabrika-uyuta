# Восстановление из бэкапа

Бэкап делает `deploy/backup.sh` каждую ночь (cron в шапке скрипта). Файлы лежат в `/opt/fabrika/backups/` 14 дней, копия уходит в S3-совместимое хранилище, если есть `/opt/fabrika/backup.env`:

- `db-<время>.dump`: `pg_dump -Fc` базы;
- `media-<время>.tar.gz`: содержимое тома `fabrika_media`.

Шаги ниже проверены на чистых контейнерах: заявки, контент и файлы media возвращаются полностью.

## 1. Взять бэкап

Локальная копия: самые свежие `db-*.dump` и `media-*.tar.gz` в `/opt/fabrika/backups/`.

Из хранилища (переменные из `/opt/fabrika/backup.env`):

```sh
. /opt/fabrika/backup.env
mkdir -p /opt/fabrika/restore
docker run --rm -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION \
  -v /opt/fabrika/restore:/restore amazon/aws-cli --endpoint-url "$S3_ENDPOINT" \
  s3 cp "s3://$S3_BUCKET/" /restore/ --recursive --exclude "*" \
  --include "db-<время>.dump" --include "media-<время>.tar.gz"
```

## 2. Поднять пустой стек (только для нового VPS)

1. Docker с плагином compose; DNS-запись домена на IP сервера.
2. `git clone <repo> /opt/fabrika/app`.
3. `/opt/fabrika/app/.env` и `/opt/fabrika/app/google-sa.json` из хранилища секретов.
4. `/opt/fabrika/app/deploy/deploy.sh`: создаёт пустую базу и тома.

## 3. Восстановить

```sh
BACKUP=/opt/fabrika/backups   # или /opt/fabrika/restore
STAMP=<время из имени файла>

# Приложение не пишет в базу, пока идёт восстановление.
docker stop fabrika-backend-1 fabrika-worker-1 fabrika-frontend-1

docker exec -i fabrika-db-1 sh -c \
  'pg_restore --clean --if-exists --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  < "$BACKUP/db-$STAMP.dump"

docker run --rm -v fabrika_media:/media -v "$BACKUP:/backup:ro" alpine:3 \
  sh -c "rm -rf /media/* && tar -xzf /backup/media-$STAMP.tar.gz -C /media"

/opt/fabrika/app/deploy/deploy.sh
```

`deploy.sh` снова прогонит release-шаг (`migrate` дотянет схему, если бэкап старше кода) и дождётся healthy.

## 4. Проверить

1. `deploy/smoke.sh https://<domain>` проходит.
2. В админке список заявок совпадает с ожидаемым, последние заявки на месте.
3. Фото на главной и в галерее открываются.
4. Заявки со статусом «Ожидает отправки» уходят в таблицу: воркер допишет недостающие строки, дублей не будет (проверка ID в колонке A).

## Мониторинг

Внешний сервис (например, Uptime Kuma или любой сервис проверки доступности) опрашивает `https://<domain>/healthz` раз в минуту и шлёт алерт, если ответ не 200 дольше 5 минут. `/healthz` фронтенда отвечает 503, когда недоступен бэкенд, база или воркер перестал писать heartbeat.
