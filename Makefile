ifneq (,$(wildcard ./.env))
include .env
export
ENV_FILE_PARAM = --env-file .env

endif

build:
	docker compose up --build -d --remove-orphans

up:
	docker compose up -d

down:
	docker compose down

show-logs:
	docker compose logs

migrate:
	docker compose exec reviews_api python manage.py migrate

makemigrations:
	docker compose exec reviews_api python manage.py makemigrations

superuser:
	docker compose exec reviews_api python manage.py createsuperuser

collectstatic:
	docker compose exec reviews_api python manage.py collectstatic --no-input --clear

down-v:
	docker compose down -v

volume:
	docker volume inspect user_management_postgres_data


user-db:
	docker compose exec postgres-db psql --username=admin --dbname=tennis_db

test:
	docker compose exec reviews_api pytest -p no:warnings --cov=.

test-html:
	docker compose exec reviews_api pytest -p no:warnings --cov=. --cov-report html

flake8:
	docker compose exec reviews_api flake8 .

black-check:
	docker compose exec reviews_api black --check --exclude=migrations .

black-diff:
	docker compose exec reviews_api black --diff --exclude=migrations .

black:
	docker compose exec reviews_api black --exclude=migrations .

isort-check:
	docker compose exec reviews_api isort ./ --check-only --skip env --skip migrations

isort-diff:
	docker compose exec reviews_api isort . --diff --skip env --skip migrations

isort:
	docker compose exec reviews_api isort . --skip env --skip migrations