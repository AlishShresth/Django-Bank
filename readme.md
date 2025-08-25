make build
make up
make down
make makemigrations
make migrate
docker compose -f local.yml exec postgres backup.sh
docker compose -f local.yml exec postgres restore.sh file_name