#!/usr/bin/env sh
# Deploy production on the VPS (tech.md, 16.3). Run it from the repository clone:
#   cd /opt/fabrika/app && git pull && deploy/deploy.sh
# Settings come from .env next to compose.prod.yml. Rollback: check out an older
# tag or commit and run this again; migrations only ever extend the schema (15.1).
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

[ -f .env ] || {
	echo "no .env next to compose.prod.yml: cp .env.example .env and fill it in" >&2
	exit 1
}

# Legal texts must be final before the site goes live (tech.md, 13.2).
if grep -rl "LEGAL_TEXT_PENDING" frontend/src >/dev/null 2>&1; then
	echo "LEGAL_TEXT_PENDING found, production stays as it is:" >&2
	grep -rl "LEGAL_TEXT_PENDING" frontend/src >&2
	exit 1
fi

# Without the file Docker would mount a directory over the key path.
[ -e google-sa.json ] || : >google-sa.json

compose() { docker compose -f compose.prod.yml "$@"; }

echo "==> build"
compose build

# A failed release step exits here; the running containers stay untouched.
echo "==> release: checks, migrations, cache table, reference data"
compose run --rm release

echo "==> up"
compose up -d --remove-orphans --wait --wait-timeout 300

domain="$(sed -n 's/^DOMAIN=//p' .env | head -n 1)"
if [ -n "$domain" ]; then
	echo "==> smoke"
	deploy/smoke.sh "https://$domain"
fi

echo "==> production runs $(git rev-parse --short HEAD)"
