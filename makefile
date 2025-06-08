docker-compose exec web alembic upgrade head

docker-compose exec web alembic revision --autogenerate -m "Init"

docker exec -it db psql -U postgres


docker-compose up --build


