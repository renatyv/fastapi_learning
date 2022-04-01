import pytest
import sqlalchemy as sqlalchemy
from sqlalchemy.future import Connection

import blog.model.user as user


# import os

@pytest.fixture()
def empty_inmemory_table_connection() -> Connection:
    """setup inmemory database and create table"""
    sqlite_engine = sqlalchemy.create_engine('sqlite://')
    connection = sqlite_engine.connect()
    connection.execute("""
    CREATE TABLE blog_user(
        user_id INTEGER PRIMARY KEY,
        password_hash VARCHAR(300),
        email VARCHAR(254),
        username VARCHAR(100) UNIQUE,
        name VARCHAR(200),
        surname VARCHAR(200));""")
    yield connection
    # teardown
    connection.close()


@pytest.fixture()
def three_users_inmemory_table_connection(empty_inmemory_table_connection) -> Connection:
    """insert three test users"""
    filled_table_conn = empty_inmemory_table_connection
    filled_table_conn.execute("""
    INSERT INTO blog_user(username, email, password_hash, name, surname)
    VALUES
        ('renatyv', 'renatyv@gmail.com', 'password_hash_renat', 'Renat', 'Yuldashev'),
        ('maratyv', 'maratyv@gmail.com', 'password_hash_marat', 'Marat', 'Yuldashev'),
        ('putin', 'putin@russia.ru', 'password_hash_putin', 'Vladimir', 'Putin');""")
    return filled_table_conn


def test_get_all_users(three_users_inmemory_table_connection):
    """assuming the test db has more than one row in blog_user table"""
    users = user.get_all_users(three_users_inmemory_table_connection)
    assert len(users) > 0


def test_get_user_1(three_users_inmemory_table_connection):
    # user with this ID should exist
    user_id = 1
    found_user = user.get_user_by_id(user_id, three_users_inmemory_table_connection)
    assert found_user.user_info.user_id == user_id


def test_create_new_user(empty_inmemory_table_connection):
    # keyword arguments are used for creation because of Pydantic
    created_user = user.create_user(empty_inmemory_table_connection,
                                    username='marat', password_hash='marats_phash')
    found_user = user.get_user_by_id(created_user.user_info.user_id, empty_inmemory_table_connection)
    assert found_user == created_user


def test_create_dublicate_user(empty_inmemory_table_connection):
    with pytest.raises(user.DuplicateUserCreationException):
        user.create_user(empty_inmemory_table_connection, username='renatyv', password_hash='ph_renatyv')
        assert user.create_user(empty_inmemory_table_connection, username='renatyv', password_hash='ph_renatyv')


def test_update_nonexistent_user(empty_inmemory_table_connection):
    with pytest.raises(user.UserNotFoundException):
        user.update_user(user_id=1,
                         username='renat',
                         surname='iuldashev',
                         db_connection=empty_inmemory_table_connection)


def test_update_user(three_users_inmemory_table_connection):
    new_surname = 'iuldashev'
    user.update_user(user_id=1,
                     surname=new_surname,
                     db_connection=three_users_inmemory_table_connection)
    updated_user = user.get_user_by_id(user_id=1, db_connection=three_users_inmemory_table_connection)
    assert updated_user.user_info.surname == new_surname


def test_delete_inexistent_user(empty_inmemory_table_connection):
    """delete user by id"""
    with pytest.raises(user.UserNotFoundException):
        user.delete_user(user_id=0, db_connection=empty_inmemory_table_connection)


def test_delete_user(three_users_inmemory_table_connection):
    deleted_user = user.delete_user(user_id=1, db_connection=three_users_inmemory_table_connection)
    assert user.get_user_by_id(user_id=1, db_connection=three_users_inmemory_table_connection) is None
