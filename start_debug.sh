echo 'activating venv'
source venv/bin/activate

echo 'running unit tests'
# python3 -m is used instead of 'pytest tests/' to include source directory into python path
#--tb=no, don't show long code parts if exception raised when running test (no tracebacks)
#--asyncio-mode=strict all async tests and fixtures must be marketed with pytest_asyncio
python3 -m pytest --no-header --tb=no --asyncio-mode=strict tests/

echo 'building containers'
docker-compose -f docker-compose.yml -f config/docker-compose-debug.yml build

echo 'starting database & web api in docker'
docker-compose -f docker-compose.yml -f config/docker-compose-debug.yml up -d

echo 'sleeping for 2s before starting api tests'
sleep 2

echo 'Check that API is alive'
python3 -m pytest --no-header --tb=no tests_api/

echo 'connecting to the containers to see logs'
docker-compose -f docker-compose.yml -f config/docker-compose-debug.yml logs -f
