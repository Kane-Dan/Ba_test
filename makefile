.PHONY: migrate create-migration db-shell up

migrate:
	docker-compose exec web alembic upgrade head

create-migration:
	docker-compose exec web alembic revision --autogenerate -m "Init"

db-shell:
	docker exec -it db psql -U postgres

up:
	docker-compose up --build
	