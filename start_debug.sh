echo 'running unit tests'
# python3 -m is used instead of 'pytest tests/' to include source directory into python path
#--tb=no, don't show long code parts if exception raised when running test (no tracebacks)
#--asyncio-mode=strict all async tests and fixtures must be marketed with pytest_asyncio
poetry run pytest --no-header --tb=no --asyncio-mode=strict tests/
if [[ $? -ne 0 ]] ; then
    exit 1
fi

echo "Running code style checks"
flake8 blog/ --max-line-length 120  --statistics
if [[ $? -ne 0 ]] ; then
    exit 1
fi
flake8 tests/ --max-line-length 120  --statistics
flake8 tests_api/ --max-line-length 120  --statistics

echo 'building containers'
docker-compose -f docker-compose.yml -f config/docker-compose-debug.yml build
if [[ $? -ne 0 ]] ; then
    exit 1
fi

echo 'starting database & web api in docker'
docker-compose -f docker-compose.yml -f config/docker-compose-debug.yml up -d
if [[ $? -ne 0 ]] ; then
    exit 1
fi

echo 'sleeping for 2s before starting api tests'
sleep 2

echo 'Check that API is alive'
poetry run pytest --no-header --tb=no tests_api/
echo 'running unit tests'
# python3 -m is used instead of 'pytest tests/' to include source directory into python path
#--tb=no, don't show long code parts if exception raised when running test (no tracebacks)
#--asyncio-mode=strict all async tests and fixtures must be marketed with pytest_asyncio
poetry run pytest --no-header --tb=no --asyncio-mode=strict tests/
if [[ $? -ne 0 ]] ; then
    exit 1
fi

echo 'connecting to the containers to see logs'
docker-compose -f docker-compose.yml -f config/docker-compose-debug.yml logs -f
