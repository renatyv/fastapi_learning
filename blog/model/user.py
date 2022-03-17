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

users = [User(**user_dict) for user_dict in users_data]


def get_all_users(skip: int, limit: int) -> list[User]:
    """return 'limit' number users starting from 'skip'"""
    return users[skip:skip+limit]


def get_user_by_id(user_id: int) -> Optional[User]:
    """find user by his id"""
    found_users = [user for user in users if user.user_id == user_id]
    if found_users:
        return found_users[0]
    else:
        return None
