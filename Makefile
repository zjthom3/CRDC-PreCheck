COMPOSE_FILE := infra/docker/compose.yml

.PHONY: dev down migrate seed test lint fmt

dev:
	docker compose -f $(COMPOSE_FILE) up --build

down:
	docker compose -f $(COMPOSE_FILE) down --remove-orphans

migrate:
	docker compose -f $(COMPOSE_FILE) run --rm api alembic -c infra/db/alembic.ini upgrade head

seed:
	docker compose -f $(COMPOSE_FILE) run --rm api python scripts/seed_synthetic.py

test:
	pytest -q

lint:
	ruff check .
	black --check .

fmt:
	ruff check . --fix
	black .
