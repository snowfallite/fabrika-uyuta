#!/usr/bin/env sh
# Deploy one environment (tech.md, 16.3): deploy.sh <staging|production> <tag>
# Needs GHCR_OWNER in the environment (lowercase GitHub owner). Rollback: run with an older tag.
set -eu

env_name="${1:?usage: deploy.sh <staging|production> <tag>}"
tag="${2:?usage: deploy.sh <staging|production> <tag>}"
case "$env_name" in staging | production) ;; *) echo "unknown environment: $env_name" >&2; exit 1 ;; esac
: "${GHCR_OWNER:?set GHCR_OWNER}"

export TAG="$tag" STACK="fabrika-$env_name" ENV_DIR="/opt/fabrika/$env_name" GHCR_OWNER
here="$(cd "$(dirname "$0")" && pwd)"
compose() { docker compose -p "$STACK" -f "$here/compose.yml" --env-file "$ENV_DIR/.env" "$@"; }

docker network create edge >/dev/null 2>&1 || true

echo "==> pull $tag"
compose pull

# A failed release step exits here; the running containers stay untouched.
echo "==> release: checks, migrations, cache table, reference data"
compose run --rm backend python manage.py release

echo "==> up"
compose up -d --remove-orphans --wait --wait-timeout 120

echo "==> $STACK runs $tag"
