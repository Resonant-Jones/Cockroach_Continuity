.PHONY: bootstrap lint typecheck test up down smoke

bootstrap:
	python -m pip install -e '.[dev]'

lint:
	ruff check src tests

typecheck:
	mypy src

test:
	pytest

up:
	docker compose up --build -d

down:
	docker compose down -v

smoke:
	curl --fail http://localhost:8000/health/live
	curl --fail http://localhost:8000/health/ready
