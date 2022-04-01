import requests
from loguru import logger
from starlette import status

API_HOST = '127.0.0.1'
API_PORT = 8100
API_ROOT = '/api/v1'
API_URL = f'http://{API_HOST}:{API_PORT}{API_ROOT}'


def test_get_all_users():
    response = requests.get(f'{API_URL}/users')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0


def test_get_all_posts():
    response = requests.get(f'{API_URL}/posts')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0
