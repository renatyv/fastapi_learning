import pytest
import sqlalchemy as sqlalchemy
from sqlalchemy.engine import Connection
import blog.model.user as user


CREATE_USER_TABLE = """CREATE TABLE blog_user(
                user_id INTEGER PRIMARY KEY,
                password_hash VARCHAR(300),
                email VARCHAR(254),
                username VARCHAR(100) UNIQUE,
                name VARCHAR(200),
                surname VARCHAR(200));"""

ADD_THREE_USERS = """INSERT INTO blog_user(username, email, password_hash, name, surname)
    VALUES
        ('renatyv', 'renatyv@gmail.com', 'password_hash_renat', 'Renat', 'Yuldashev'),
        ('maratyv', 'maratyv@gmail.com', 'password_hash_marat', 'Marat', 'Yuldashev'),
        ('putin', 'putin@russia.ru', 'password_hash_putin', 'Vladimir', 'Putin');"""


@pytest.fixture()
def empty_inmemory_table_connection() -> Connection:
    """setup inmemory database and create table"""
    sqlite_engine = sqlalchemy.create_engine('sqlite://')
    with sqlite_engine.connect() as connection:
        connection.execute(CREATE_USER_TABLE)
        yield connection


@pytest.fixture()
def three_users_inmemory_table_connection(empty_inmemory_table_connection) -> Connection:
    """insert three test users"""
    filled_table_conn = empty_inmemory_table_connection
    filled_table_conn.execute(ADD_THREE_USERS)
    return filled_table_conn


def test_get_user_1(three_users_inmemory_table_connection):
    # user with this ID should exist
    user_id = 1
    found_user = user.get_user_by_id(user_id, three_users_inmemory_table_connection)
    assert found_user.user_id == user_id


def test_create_new_user(empty_inmemory_table_connection):
    new_user_info = user.UserInfo(username='maratyv',
                                  email='maratyv@gmail.com',
                                  name='Marat',
                                  surname='Iuldashev')
    created_user = user.create_user(empty_inmemory_table_connection,
                                    user.UserCreationData(password='maratyv',
                                                          user_info=new_user_info))
    found_user = user.get_user_by_id(created_user.user_id, empty_inmemory_table_connection)
    assert found_user == created_user


def test_create_dublicate_user(empty_inmemory_table_connection):
    with pytest.raises(user.DuplicateUserCreationException):
        new_user_info = user.UserInfo(username='maratyv',
                                      email='maratyv@gmail.com',
                                      name='Marat',
                                      surname='Iuldashev')
        user_creation_data = user.UserCreationData(password='maratyv',
                                                   user_info=new_user_info)
        user.create_user(empty_inmemory_table_connection, user_creation_data)
        assert user.create_user(empty_inmemory_table_connection, user_creation_data)


def test_update_nonexistent_user(empty_inmemory_table_connection):
    with pytest.raises(user.UserNotFoundException):
        new_user_info = user.UserInfo(username='renatyv',
                                      email='renatyv@gmail.com',
                                      name='Renat',
                                      surname='iuldashev')
        user.update_user_info(empty_inmemory_table_connection,
                              user_id=1,
                              user_info=new_user_info)


def test_update_user(three_users_inmemory_table_connection):
    new_user_info = user.UserInfo(username='renatyv',
                                  email='renatyv@gmail.com',
                                  name='Renat',
                                  surname='iuldashev')
    user.update_user_info(user_id=1,
                          user_info=new_user_info,
                          db_connection=three_users_inmemory_table_connection)
    updated_user = user.get_user_by_id(user_id=1, db_connection=three_users_inmemory_table_connection)
    assert updated_user.user_info.surname == new_user_info.surname


def test_delete_nonexistent_user(empty_inmemory_table_connection):
    """delete user by id"""
    with pytest.raises(user.UserNotFoundException):
        user.delete_user(user_id=0, db_connection=empty_inmemory_table_connection)


def test_delete_user(three_users_inmemory_table_connection):
    user.delete_user(user_id=1, db_connection=three_users_inmemory_table_connection)
    assert user.get_user_by_id(user_id=1, db_connection=three_users_inmemory_table_connection) is None
