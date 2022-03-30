import requests
from blog.http_status_codes import HttpStatusCode as codes

API_HOST = '127.0.0.1'
API_PORT = 8100
API_ROOT = '/api/v1'
API_URL = f'http://{API_HOST}:{API_PORT}{API_ROOT}'


def test_get_all_users():
    response = requests.get(f'{API_URL}/users')
    assert response.status_code == codes.OK.value
    assert len(response.json()) > 0
