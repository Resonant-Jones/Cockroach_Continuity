.PHONY: bootstrap lint typecheck test up down smoke migrate downgrade migration-sql

bootstrap:
	python -m pip install -e '.[dev]'

lint:
	ruff check src tests

typecheck:
	mypy src

test:
	pytest

migrate:
	alembic upgrade head

downgrade:
	alembic downgrade base

migration-sql:
	alembic upgrade head --sql

up:
	docker compose up --build -d

down:
	docker compose down -v

smoke:
	curl --fail http://localhost:8000/health/live
	curl --fail http://localhost:8000/health/ready
