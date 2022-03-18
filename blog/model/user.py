from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    name: str
    surname: str


users_data = [{"user_id": 0, "name": "Renat", "surname": "Yuldashev"},
              {"user_id": 1, "name": "Vlada", "surname": "Yuldasheva"},
              {"user_id": 2, "name": "Ivan", "surname": "Sudos"}
              ]

local_users = [User(**user_dict) for user_dict in users_data]


def get_all_users(skip: int, limit: int, users=None) -> list[User]:
    """return 'limit' number users starting from 'skip'"""
    if users is None:
        users = local_users
    return users[skip:skip + limit]


def get_user_by_id(user_id: int, users=None) -> Optional[User]:
    """find user by his id"""
    if users is None:
        users = local_users
    found_users = [user for user in users if user.user_id == user_id]
    if found_users:
        return found_users[0]
    else:
        return None


class DuplicateUserCreationException(Exception):
    pass


def create_user(username: str, surname: str, users=None) -> User:
    """adds new user to the database. If pair (name,surname) is already in db, raises exception
    :raises DuplicateUserCreationException"""
    if users is None:
        users = local_users

    found_user_ids = [user.user_id for user in users if (user.name == username and user.surname == surname)]
    if not found_user_ids:
        new_user = User(user_id=len(users), name=username, surname=surname)
        users.append(new_user)
        return new_user
    else:
        raise DuplicateUserCreationException(f'User {username} {surname} already exists with user_id={found_user_ids}')
