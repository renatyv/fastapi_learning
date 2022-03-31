import requests
from blog.http_status_codes import HttpStatusCode as codes
from loguru import logger

API_HOST = '127.0.0.1'
API_PORT = 8100
API_ROOT = '/api/v1'
API_URL = f'http://{API_HOST}:{API_PORT}{API_ROOT}'


def test_get_all_users():
    response = requests.get(f'{API_URL}/users')
    assert response.status_code == codes.OK.value
    assert len(response.json()) > 0


def test_get_user():
    user_id = 2
    response = requests.get(f'{API_URL}/users/{user_id}')
    print(response.json())
    assert response.status_code == codes.FOUND.value
    assert len(response.json()) > 0
    assert response.json().get('user_id', -1) == user_id


def test_get_all_posts():
    response = requests.get(f'{API_URL}/posts')
    assert response.status_code == codes.OK.value
    assert len(response.json()) > 0


def test_get_post():
    post_id = 2
    response = requests.get(f'{API_URL}/posts/{post_id}')
    print(response.json())
    assert response.status_code == codes.FOUND.value
    assert len(response.json()) > 0
    assert response.json().get('post_id', -1) == post_id