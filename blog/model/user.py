from typing import Optional

from retry import retry
from sqlalchemy.exc import IntegrityError
import sqlalchemy.engine
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import Connection, LegacyCursorResult, Result
from sqlalchemy.ext.asyncio import AsyncConnection
from loguru import logger


class VisibleUserInfo(BaseModel):
    user_id: int
    username: str
    name: Optional[str]
    surname: Optional[str]
    email: Optional[str]


class User(BaseModel):
    user_info: VisibleUserInfo
    password_hash: str


async def get_all_users_async(db_connection: AsyncConnection, skip: int = 0, limit: int = 10 ** 6) -> list[User]:
    """return 'limit' number users starting from 'skip'"""
    users = []
    statement = text("""SELECT
        user_id, username, name, surname, email, password_hash
    FROM blog_user
    LIMIT :limit OFFSET :skip""")
    params = {'skip': skip, 'limit': limit}
    async with db_connection.begin():  # within transaction
        result: Result = await db_connection.execute(statement, parameters=params)
        rows = result.all()
        for user_id, username, name, surname, email, password_hash in rows:
            users.append(User(
                user_info=VisibleUserInfo(user_id=user_id,
                                          username=username,
                                          name=name,
                                          surname=surname,
                                          email=email),
                password_hash=password_hash))
    return users


def get_user_by_id(user_id: int, db_connection: Connection) -> Optional[User]:
    """find user by his id
    :returns User object, if user is found in database
    :returns None if user is not found"""
    with db_connection.begin():  # within transaction
        try:
            statement = text(
                """SELECT user_id, username, name, surname, email, password_hash
                FROM blog_user
                WHERE user_id = :user_id""")
            params = {'user_id': user_id}
            rows = db_connection.execute(statement, **params).fetchall()
        except Exception:
            logger.exception('Unknown DB query error')
            return None
        else:
            for user_id, username, name, surname, email, password_hash in rows:
                return User(user_info=VisibleUserInfo(user_id=user_id,
                                                      username=username,
                                                      name=name,
                                                      surname=surname,
                                                      email=email),
                            password_hash=password_hash)


def get_user_by_username(username: str, db_connection: Connection) -> Optional[User]:
    """find user by his username
    :returns User object, if user is found in database
    :returns None if user is not found"""
    with db_connection.begin():  # within transaction
        try:
            statement = text("""SELECT
                                    user_id, username, name, surname, email, password_hash
                                FROM blog_user
                                WHERE username = :username""")
            params = {'username': username}
            rows = db_connection.execute(statement, **params).fetchall()
        except Exception:
            logger.exception('Unknown DB query error')
            return None
        else:
            for user_id, username, name, surname, email, password_hash in rows:
                return User(user_info=VisibleUserInfo(user_id=user_id,
                                                      username=username,
                                                      name=name,
                                                      surname=surname,
                                                      email=email),
                            password_hash=password_hash)
            return None


class DuplicateUserCreationException(Exception):
    pass


class UnknownException(Exception):
    pass


def create_user(db_connection: Connection,
                username: str,
                password_hash: str,
                email: Optional[str] = None,
                name: Optional[str] = None,
                surname: Optional[str] = None) -> User:
    """adds new user to the database. If email is already in db, raises exception
    saves hashed password
    :raises DuplicateUserCreationException if user with such name and surname exists already
    :raises UnknownException if smth went wrong while creating the user"""
    with db_connection.begin():  # within transaction
        try:
            statement = text("""INSERT INTO blog_user(username, email, password_hash, name, surname)
                                VALUES (:username, :email, :password_hash, :name, :surname)
                                RETURNING user_id""")
            params = {'username': username, 'email': email, 'password_hash': password_hash, 'name': name,
                      'surname': surname}
            row: sqlalchemy.engine.Row = db_connection.execute(statement, params).fetchone()
            user_id = row[0]
        except IntegrityError as ie:
            raise DuplicateUserCreationException(str(ie))
        except Exception as e:
            logger.exception('Unknown DB query error')
            raise UnknownException(e)
        else:
            return User(
                user_info=VisibleUserInfo(user_id=user_id,
                                          username=username,
                                          name=name,
                                          surname=surname,
                                          email=email),
                password_hash=password_hash)


class UserNotFoundException(Exception):
    pass


@retry(exceptions=IntegrityError)
def update_user(db_connection: Connection,
                user_id: int,
                username: Optional[str] = None,
                name: Optional[str] = None,
                surname: Optional[str] = None,
                email: Optional[str] = None,
                password_hash: Optional[str] = None) -> User:
    """Updates user info in database.
    :returns User object if update was successful
    :raises UserNotFoundException if user_id is invalid"""
    with db_connection.begin():  # start transaction
        user_to_update = get_user_by_id(user_id, db_connection)
        if not user_to_update:
            raise UserNotFoundException()
        if username:
            user_to_update.user_info.username = username
        if name:
            user_to_update.user_info.name = name
        if surname:
            user_to_update.user_info.surname = surname
        if email:
            user_to_update.user_info.email = email
        if password_hash:
            user_to_update.password_hash = password_hash
        try:
            statement = text("""UPDATE blog_user
                                SET
                                    username = :username,
                                    name = :name,
                                    surname = :surname,
                                    email = :email,
                                    password_hash = :password_hash
                                WHERE user_id = :user_id
                                RETURNING username, name, surname, email, password_hash""")
            params = {'username': user_to_update.user_info.username,
                      'name': user_to_update.user_info.name,
                      'surname': user_to_update.user_info.surname,
                      'email': user_to_update.user_info.email,
                      'password_hash': user_to_update.password_hash,
                      'user_id': user_id}
            row = db_connection.execute(statement, params).fetchone()
        except Exception:
            logger.exception('Unknown DB query error')
            raise UnknownException()
        else:
            if row is None:
                raise UnknownException()
            else:
                username, name, surname, email, password_hash = row
                return User(user_info=VisibleUserInfo(user_id=user_id,
                                                      username=username,
                                                      name=name,
                                                      surname=surname,
                                                      email=email),
                            password_hash=password_hash)


def delete_user(user_id: int, db_connection: Connection):
    """Delete user by user_id. Note, that all user posts will be deleted with CASCADE,
    :raises UserNotFoundException if nothing is deleted from database"""
    with db_connection.begin():  # within transaction
        try:
            statement = text("""DELETE FROM blog_user WHERE user_id = :user_id""")
            params = {'user_id': user_id}
            result: LegacyCursorResult = db_connection.execute(statement, params)
            deleted_rows = result.rowcount
        except Exception as e:
            logger.exception('Unknown DB query error')
            raise UnknownException(e)
        else:
            if deleted_rows == 0:
                raise UserNotFoundException()
            if deleted_rows > 1:
                logger.error(f'Many users with user_id={user_id} were deleted')
