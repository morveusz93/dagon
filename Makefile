.PHONY: start test lint format docker-build docker-run

start:
	poetry run python main.py

format:
	poetry run isort . && poetry run black .

docker-build:
	docker build -t dagon_bot:latest .

docker-run:
	docker run --rm --env-file .env dagon_bot:latest

test:
	poetry run pytest -q

lint:
	poetry run black --check . && poetry run isort --check-only .
