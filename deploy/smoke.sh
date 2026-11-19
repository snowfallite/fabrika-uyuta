#!/usr/bin/env sh
# Post-deploy smoke test (tech.md, 16.3 and S1-10 AC2): smoke.sh <base url>
# SMOKE_ENV=production|e2e overrides the guess from the host name.
set -eu

base="${1:?usage: smoke.sh <base url>}"
base="${base%/}"
env_name="${SMOKE_ENV:-}"
if [ -z "$env_name" ]; then
	case "$base" in *://localhost* | *://127.0.0.1*) env_name=e2e ;; *) env_name=production ;; esac
fi

fetch() { curl -sS --max-time 20 "$@"; }
fail() {
	echo "FAIL: $*" >&2
	exit 1
}
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
	echo "$robots" | grep -q '^Clean-param: product /lead$' ||
		fail "robots.txt has no Clean-param in production"
else
	echo "$robots" | grep -q '^Disallow: /$' || fail "robots.txt must disallow everything outside production"
fi
echo "ok   robots.txt ($env_name)"

# S2-18 AC1: the www host exists only in production, where Caddy answers it with one redirect.
if [ "$env_name" = production ]; then
	www="$(printf '%s' "$base" | sed 's#://#://www.#')"
	code="$(fetch -o /dev/null -w '%{http_code}' "$www/privacy")"
	target="$(fetch -o /dev/null -w '%{redirect_url}' "$www/privacy")"
	[ "$code" = 301 ] || fail "www answered $code, expected 301"
	[ "$target" = "$base/privacy" ] || fail "www points at $target, expected $base/privacy"
	echo "ok   www -> $target"
fi

echo "smoke passed: $base"
