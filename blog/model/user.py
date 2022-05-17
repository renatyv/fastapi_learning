import asyncio
from typing import Optional

from retry import retry
from sqlalchemy.exc import IntegrityError
import sqlalchemy.engine
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import text
from sqlalchemy.engine import Connection, Result, CursorResult
from sqlalchemy.ext.asyncio import AsyncConnection
from loguru import logger

from blog.model.auth.user_password import hash_password


class UserInfo(BaseModel):
    username: str = Field(...,  # required, no default value. = None to make optional
                          min_length=1,
                          max_length=250)
    email: Optional[EmailStr] = EmailStr(None)
    name: Optional[str] = Field(None, max_length=100)
    surname: Optional[str] = Field(None, max_length=100)


class User(BaseModel):
    user_id: int = Field(..., ge=0)
    user_info: UserInfo
    password_hash: str = Field(..., min_length=1, max_length=100)


async def get_all_users_async(db_connection: AsyncConnection, skip: int = 0, limit: int = 10 ** 6,
                              TIMEOUT=1.0) -> list[User]:
    """return 'limit' number users starting from 'skip'
    Starts and commits a new transaction.
    :raises asyncio.TimeoutError
    """
    users = []
    statement = text("""SELECT
        user_id, username, name, surname, email, password_hash
    FROM blog_user
    LIMIT :limit OFFSET :skip""")
    params = {'skip': skip, 'limit': limit}
    async with db_connection.begin():  # within transaction
        result: Result = await asyncio.wait_for(db_connection.execute(statement, parameters=params),
                                                timeout=TIMEOUT)
        rows = result.all()
        for user_id, username, name, surname, email, password_hash in rows:
            users.append(User(user_id=user_id,
                              user_info=UserInfo(username=username,
                                                 name=name,
                                                 surname=surname,
                                                 email=email),
                              password_hash=password_hash))
    return users


def get_user_by_id(user_id: int, db_connection: Connection) -> Optional[User]:
    """find user by his id
    Starts and commits a new transaction.

    :returns User object, if user is found in database
    :returns None if user is not found"""

    try:
        statement = text(
            """SELECT user_id, username, name, surname, email, password_hash
            FROM blog_user
            WHERE user_id = :user_id""")
        params = {'user_id': user_id}
        with db_connection.begin():  # within transaction
            rows = db_connection.execute(statement, **params).fetchall()
    except Exception:
        logger.exception('Unknown DB query error')
        return None
    else:
        for user_id, username, name, surname, email, password_hash in rows:
            return User(user_id=user_id,
                        user_info=UserInfo(username=username,
                                           name=name,
                                           surname=surname,
                                           email=email),
                        password_hash=password_hash)


async def get_user_by_username(username: str, db_connection: AsyncConnection) -> Optional[User]:
    """find user by his username
    Starts and commits a new transaction.

    :returns User object, if user is found in database
    :returns None if user is not found"""
    async with db_connection.begin():  # within transaction
        try:
            statement = text("""SELECT
                                    user_id, username, name, surname, email, password_hash
                                FROM blog_user
                                WHERE username = :username""")
            params = {'username': username}
            result = await db_connection.execute(statement, parameters=params)
            rows = result.fetchall()
        except Exception:
            logger.exception('Unknown DB query error')
            return None
        else:
            for user_id, username, name, surname, email, password_hash in rows:
                return User(user_id=user_id,
                            user_info=UserInfo(username=username,
                                               name=name,
                                               surname=surname,
                                               email=email),
                            password_hash=password_hash)
            return None


class DuplicateUserCreationException(Exception):
    pass


class UnknownException(Exception):
    pass


class UserCreationData(BaseModel):
    password: str = Field(..., min_length=1, max_length=300)
    user_info: UserInfo


def create_user(db_connection: Connection,
                create_user_data: UserCreationData) -> User:
    """adds new user to the database.
    If email is already in db, raises exception, saves hashed password
    Starts and commits a new transaction.

    :raises DuplicateUserCreationException if user with such name and surname exists already
    :raises UnknownException if smth went wrong while creating the user"""
    with db_connection.begin():  # within transaction
        try:
            user_info = create_user_data.user_info
            password_hash = hash_password(create_user_data.password)
            statement = text("""INSERT INTO blog_user(username, email, password_hash, name, surname)
                                VALUES (:username, :email, :password_hash, :name, :surname)
                                RETURNING user_id""")
            params = {'username': user_info.username, 'email': user_info.email,
                      'name': user_info.name,
                      'surname': user_info.surname,
                      'password_hash': password_hash}
            row: sqlalchemy.engine.Row = db_connection.execute(statement, params).fetchone()
            user_id = row[0]
        except IntegrityError as ie:
            raise DuplicateUserCreationException(str(ie))
        except Exception as e:
            logger.exception('Unknown DB query error')
            raise UnknownException(e)
        else:
            return User(user_id=user_id, user_info=user_info, password_hash=password_hash)


class UserNotFoundException(Exception):
    pass


@retry(exceptions=IntegrityError)
def update_user_info(db_connection: Connection,
                     user_id: int,
                     user_info: UserInfo) -> UserInfo:
    """Updates user info in database.
    Starts and commits a new transaction.
    :returns User object if update was successful
    :raises UserNotFoundException if user_id is invalid"""
    with db_connection.begin():  # start transaction
        try:
            statement = text("""UPDATE blog_user
                                SET
                                    username = :username,
                                    name = :name,
                                    surname = :surname,
                                    email = :email
                                WHERE user_id = :user_id
                                RETURNING username, name, surname, email""")
            params = {'username': user_info.username,
                      'name': user_info.name,
                      'surname': user_info.surname,
                      'email': user_info.email,
                      'user_id': user_id}
            row = db_connection.execute(statement, params).fetchone()
        except Exception:
            logger.exception('Unknown DB query error')
            raise UnknownException()
        else:
            if row is None:
                raise UserNotFoundException()
            else:
                username, name, surname, email = row
                return UserInfo(username=username,
                                name=name,
                                surname=surname,
                                email=email)


def delete_user(user_id: int, db_connection: Connection):
    """Delete user by user_id. Note, that all user posts will be deleted with CASCADE,
    Starts and commits a new transaction.

    :raises UserNotFoundException if nothing is deleted from database"""
    with db_connection.begin():  # within transaction
        try:
            statement = text("""DELETE FROM blog_user WHERE user_id = :user_id""")
            params = {'user_id': user_id}
            result: CursorResult = db_connection.execute(statement, params)
            deleted_rows = result.rowcount
        except Exception as e:
            logger.exception('Unknown DB query error')
            raise UnknownException(e)
        else:
            if deleted_rows == 0:
                raise UserNotFoundException()
            if deleted_rows > 1:
                logger.error(f'Many users with user_id={user_id} were deleted')
