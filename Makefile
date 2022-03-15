docker exec -ti 7db0b88cc75b /bin/bash

docker compose up --build -d --remove-orphans

docker compose logs
docker exec -ti -u root a6360e4ab2b9 /bin/bash
docker network inspect bridge

docker-compose run user_manage_api python manage.py makemigrations

docker-compose config