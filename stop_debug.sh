echo 'Removing all docker containers'
docker-compose -f docker-compose-common.yml -f docker-compose-debug.yml down