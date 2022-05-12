import pytest
import requests
from starlette import status

API_URL = 'http://127.0.0.1:8100/api/v1'


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
    response = requests.get(f'{API_URL}/posts')
    assert response.status_code == status.HTTP_200_OK
    post_id = response.json()[0].get('post_id')
    assert requests.get(f'{API_URL}/posts/{post_id}').json().get('post_id') == post_id


@pytest.fixture
def authorization_header_userid_2() -> dict[str, str]:
    """:returns {'Authorization': 'Bearer access_token'}"""
    form_data = {"username": "2", "password": "22"}
    token = requests.post(f"{API_URL}/token", data=form_data).json().get('access_token')
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


def test_create_delete_post(authorization_header_userid_2):
    response = requests.post(f"{API_URL}/posts/",
                             json={'title': 'test title',
                                   'body': 'test body'},
                             headers=authorization_header_userid_2)
    assert response.status_code == status.HTTP_201_CREATED
    post_id: str = response.json().get('post_id')
    response = requests.delete(f"{API_URL}/posts/{post_id}",
                               headers=authorization_header_userid_2)
    assert response.status_code == status.HTTP_200_OK


def test_create_auth_delete_user():
    # create user
    username = 'renat'
    password = 'very_unusual_username1'
    response = requests.post(f"{API_URL}/users/",
                             json={'user_info': {"username": username,
                                                 "email": "user@example.com",
                                                 "name": "renat",
                                                 "surname": "u"},
                                   "password": password})
    assert response.status_code == 200
    # authenticate
    form_data = {"username": username,
                 "password": password}
    response = requests.post(f"{API_URL}/token", data=form_data)
    assert response.status_code == 200
    token = response.json().get('access_token')
    # delete user
    response = requests.delete(f'{API_URL}/users',
                               headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
