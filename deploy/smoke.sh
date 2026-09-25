#!/usr/bin/env sh
# Post-deploy smoke test (tech.md, 16.3 and S1-10 AC2): smoke.sh <base url>
# SMOKE_AUTH=user:password for staging basic auth; SMOKE_ENV=staging|production|e2e overrides
# the guess from the host name.
set -eu

base="${1:?usage: smoke.sh <base url>}"
base="${base%/}"
env_name="${SMOKE_ENV:-}"
if [ -z "$env_name" ]; then
  case "$base" in *://stage.*) env_name=staging ;; *://localhost* | *://127.0.0.1*) env_name=e2e ;; *) env_name=production ;; esac
fi

fetch() { curl -sS --max-time 20 ${SMOKE_AUTH:+-u "$SMOKE_AUTH"} "$@"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
expect_status() {
  code="$(fetch -o /dev/null -w '%{http_code}' "$base$2")"
  [ "$code" = "$1" ] || fail "$2 answered $code, expected $1"
  echo "ok   $2 -> $code"
}

expect_status 200 /
expect_status 200 /healthz
expect_status 404 /api/v1/home/
# Caddy routes Django static files to the backend, the admin path goes the same way.
expect_status 200 /django-static/admin/css/base.css

media="$(fetch "$base/" | grep -o '/media/[^" ]*\.webp' | head -n 1 || true)"
if [ -n "$media" ]; then
  fetch -I "$base$media" | grep -qi '^cache-control:.*immutable' || fail "$media is not immutable"
  echo "ok   $media immutable"
else
  echo "skip media: no photos on the home page yet"
fi

robots="$(fetch "$base/robots.txt")"
if [ "$env_name" = production ]; then
  echo "$robots" | grep -q '^Sitemap:' || fail "robots.txt has no Sitemap in production"
else
  echo "$robots" | grep -q '^Disallow: /$' || fail "robots.txt must disallow everything outside production"
fi
echo "ok   robots.txt ($env_name)"

if [ "$env_name" = staging ]; then
  fetch -I "$base/" | grep -qi '^x-robots-tag:.*noindex' || fail "staging lacks X-Robots-Tag"
  echo "ok   X-Robots-Tag"
fi
echo "smoke passed: $base"
