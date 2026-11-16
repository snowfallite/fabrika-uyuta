#!/usr/bin/env sh
# Nightly backup of the production stack (tech.md, S2-12): backup.sh
#   cron on the VPS: 30 3 * * * /opt/fabrika/app/deploy/backup.sh >> /var/log/fabrika-backup.log 2>&1
# Keeps 14 days in $BACKUP_DIR and copies each run to S3-compatible storage in Russia when
# /opt/fabrika/backup.env sets S3_ENDPOINT, S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
# (AWS_DEFAULT_REGION optional). STACK and MEDIA_VOLUME override the names for tests.
set -eu

stack="${STACK:-fabrika}"
media_volume="${MEDIA_VOLUME:-${stack}_media}"
dir="${BACKUP_DIR:-/opt/fabrika/backups}"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$dir"

echo "==> $stamp database"
# Custom format: pg_restore can restore it selectively and in parallel.
docker exec "${stack}-db-1" sh -c 'pg_dump -Fc -U "$POSTGRES_USER" "$POSTGRES_DB"' \
	>"$dir/db-$stamp.dump"

echo "==> $stamp media"
docker run --rm -v "$media_volume:/media:ro" -v "$dir:/backup" alpine:3 \
	tar -czf "/backup/media-$stamp.tar.gz" -C /media .

find "$dir" -name 'db-*.dump' -mtime +14 -delete
find "$dir" -name 'media-*.tar.gz' -mtime +14 -delete

secrets="${BACKUP_ENV:-/opt/fabrika/backup.env}"
if [ -f "$secrets" ]; then
	# shellcheck disable=SC1090  # path comes from the environment
	. "$secrets"
	for file in "db-$stamp.dump" "media-$stamp.tar.gz"; do
		docker run --rm \
			-e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
			-e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
			-e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-ru-central1}" \
			-v "$dir:/backup:ro" amazon/aws-cli \
			--endpoint-url "$S3_ENDPOINT" s3 cp "/backup/$file" "s3://$S3_BUCKET/$file"
	done
	echo "==> copied to s3://$S3_BUCKET/"
else
	echo "==> no $secrets: local copy only"
fi
echo "==> done: $dir/db-$stamp.dump, $dir/media-$stamp.tar.gz"
