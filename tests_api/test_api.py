import json
from typing import Dict

import pytest
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


def test_get_first_user():
    users = requests.get(f'{API_URL}/users').json()
    user_id = users[0].get('user_id')
    assert requests.get(f'{API_URL}/users/{user_id}').json().get('user_id') == user_id


def test_get_first_post():
    post_id = requests.get(f'{API_URL}/posts').json()[0].get('post_id')
    assert requests.get(f'{API_URL}/posts/{post_id}').json().get('post_id') == post_id


@pytest.fixture
def authorization_header_userid_2() -> dict[str, str]:
    """:returns {'Authorizatino': 'Bearer access_token'}"""
    form_data = {"username": "2", "password": "22"}
    token = requests.post("http://127.0.0.1:8100/api/v1/token", data=form_data).json().get('access_token')
    return {'Authorization': f'Bearer {token}'}


def test_update_post(authorization_header_userid_2):
    """authorize and update first post"""
    # find post by user id
    post_id = 7
    response = requests.put(f'{API_URL}/posts/{post_id}',
                            json={"title": "title123"},
                            headers=authorization_header_userid_2)
    assert response.json().get('title') == 'title123'
    assert requests.get(f"{API_URL}/posts/{response.json().get('post_id')}").json().get('title') == 'title123'