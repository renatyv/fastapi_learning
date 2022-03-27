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
    with db_connection.begin(): # within transaction
        try:
            statement = text("""SELECT user_id, name, surname FROM blog_user WHERE user_id = :user_id""")
            params = {'user_id': user_id}
            rows = db_connection.execute(statement,**params).fetchall()
        except Exception as e:
            logger.error(e)
            return None
        else:
            for user_id, name, surname in rows:
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
            return User(user_id=user_id, name=username, surname=surname)


class UserNotFoundException(Exception):
    pass


def update_user(user_id: int, name: Optional[str], surname: Optional[str], db_connection: Connection) -> User:
    """updates name or surname for a user in db.
    name and surname are optional. If they are not set, name and surname are not updated
    :returns User object if update was successful
    :raises UserNotFoundException if user_id is invalied"""
    with db_connection.begin(): # start transaction
        try:
            if name and surname:
                statement = text("""UPDATE blog_user 
                                    SET name = :name, surname = :surname 
                                    WHERE user_id = :user_id
                                    RETURNING name, surname """)
            elif not name and surname:
                statement = text("""UPDATE blog_user 
                                    SET surname = :surname 
                                    WHERE user_id = :user_id
                                    RETURNING name, surname """)
            elif name and not surname:
                statement = text("""UPDATE blog_user 
                                    SET name = :name 
                                    WHERE user_id = :user_id
                                    RETURNING name, surname """)
            else:
                statement = text("""SELECT name, surname 
                                    FROM blog_user 
                                    WHERE user_id = :user_id""")
            params = {'name': name, 'surname': surname, 'user_id': user_id}
            row = db_connection.execute(statement, params).fetchone()
        except Exception as e:
            logger.error('unknown error: {e}')
            raise UnknownException
        else:
            if row is None:
                raise UserNotFoundException()
            else:
                updated_name, updated_surname = row
                return User(user_id=user_id, name=updated_name, surname=updated_surname)
