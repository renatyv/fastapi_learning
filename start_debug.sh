echo 'activating venv'
source venv/bin/activate

echo 'running tests'
pytest

echo 'building containers'
docker-compose -f docker-compose-common.yml -f docker-compose-debug.yml build

echo 'starting database & web api in docker'
docker-compose -f docker-compose-common.yml -f docker-compose-debug.yml up
