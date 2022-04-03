echo 'Removing all docker containers'
docker-compose -f docker-compose.yml -f config/docker-compose-debug.yml down