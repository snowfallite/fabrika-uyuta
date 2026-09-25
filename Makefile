# Single entry point for dev and CI commands (tech.md, 15.4).
-include .env
export

MANAGE := cd backend && uv run python manage.py

.PHONY: dev dev-down migrations migrate gen seed fmt check-fast test gate drift guard e2e

dev:
	docker compose up -d db backend
	@echo "Frontend: pnpm -C frontend dev"

dev-down:
	docker compose down

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate
	$(MANAGE) createcachetable

gen:
	$(MANAGE) spectacular --validate --file ../contracts/openapi.yaml
	pnpm -C frontend gen:api

seed:
	$(MANAGE) sync_reference_data

fmt:
	pnpm -C frontend format
	cd backend && uv run ruff format .

check-fast:
	pnpm -C frontend check
	cd backend && uv run mypy

test:
	pnpm -C frontend test:unit
	cd backend && uv run pytest

gate:
	pnpm -C frontend format:check
	pnpm -C frontend lint
	pnpm -C frontend check
	pnpm -C frontend knip
	pnpm -C frontend test:unit
	pnpm -C frontend build
	cd backend && uv run ruff format --check .
	cd backend && uv run ruff check .
	cd backend && uv run mypy
	$(MANAGE) makemigrations --check --dry-run
	cd backend && uv run pytest
	$(MAKE) drift
	$(MAKE) guard

drift: gen
	git diff --exit-code contracts/openapi.yaml frontend/src/lib/types/api.d.ts

guard:
	uvx pytest scripts/ -q
	uv run --no-project python scripts/contract_guard.py --base main

e2e:
	E2E_BASE_URL=http://localhost:5173 pnpm -C frontend test:e2e
