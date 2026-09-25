# Single entry point for dev and CI commands (tech.md, 15.4).
-include .env
export

MANAGE := cd backend && uv run python manage.py
E2E := docker compose -f compose.e2e.yml

.PHONY: dev dev-down migrations migrate gen seed fmt check-fast test gate drift guard e2e e2e-down

dev:
	docker compose up -d db backend worker
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
	$(MANAGE) seed_demo

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
	CI=1 pnpm -C frontend test:unit
	pnpm -C frontend build
	cd backend && uv run ruff format --check .
	cd backend && uv run ruff check .
	cd backend && uv run mypy
	$(MANAGE) makemigrations --check --dry-run
	cd backend && uv run pytest --hypothesis-profile=ci
	$(MAKE) drift
	$(MAKE) guard

drift: gen
	git diff --exit-code contracts/openapi.yaml frontend/src/lib/types/api.d.ts

guard:
	uvx pytest scripts/ -q
	uv run --no-project python scripts/contract_guard.py --base main

e2e:
	$(E2E) up --build --wait
	$(E2E) exec -T backend python manage.py seed_demo
	pnpm -C frontend test:e2e

e2e-down:
	$(E2E) down -v
