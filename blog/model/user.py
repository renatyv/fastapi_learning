import sqlite3
from typing import Optional

from sqlalchemy.exc import IntegrityError
import sqlalchemy.engine
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import Connection
from loguru import logger


class User(BaseModel):
    user_id: int
    name: str
    surname: str


def get_all_users(db_connection: Connection, skip: int = 0, limit: int = 10**6) -> list[User]:
    """return 'limit' number users starting from 'skip'"""
    users = []
    with db_connection.begin(): # within transaction
        statement = text('SELECT user_id, name, surname FROM blog_user LIMIT :limit OFFSET :skip')
        params = {'skip': skip, 'limit': limit}
        rows = db_connection.execute(statement,**params).fetchall()
        for user_id, name, surname in rows:
            users.append(User(user_id=user_id,name=name,surname=surname))
    return users


def get_user_by_id(user_id: int, db_connection: Connection) -> Optional[User]:
    """find user by his id"""
    logger.debug(f'Looking for user {user_id}')
    with db_connection.begin(): # within transaction
        try:
            statement = text("""SELECT user_id, name, surname FROM blog_user WHERE user_id = :user_id""")
            params = {'user_id': user_id}
            rows = db_connection.execute(statement,**params).fetchall()
        except Exception as e:
            logger.error(e)
            return None
        else:
            logger.debug(f'Query successful, {rows}')
            for user_id, name, surname in rows:
                logger.debug(f'{(user_id, name, surname)}')
                return User(user_id=user_id, name=name, surname=surname)


class DuplicateUserCreationException(Exception):
    pass


class UnknownException(Exception):
    pass


def create_user(username: str, surname: str, db_connection: Connection) -> User:
    """adds new user to the database. If pair (name,surname) is already in db, raises exception
    :raises DuplicateUserCreationException if user with such name and surname exists already
    :raises UnknownException if smth went wrong while creating the user"""
    with db_connection.begin():  # within transaction
        try:
            statement = text("""INSERT INTO blog_user(name, surname) VALUES (:username, :surname) RETURNING user_id""")
            params = {'username': username, 'surname': surname}
            row: sqlalchemy.engine.Row = db_connection.execute(statement,params).fetchone()
            user_id = row[0]
        except IntegrityError as ie:
            raise DuplicateUserCreationException(str(ie))
        except Exception as e:
            logger.error(e)
            raise UnknownException(e)
        else:
            logger.debug(f'user with id {user_id} created')
            return User(user_id=user_id, name=username, surname=surname)
