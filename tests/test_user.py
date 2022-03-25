import pytest
import sqlalchemy as sqlalchemy

import blog.model.user as user
# import os

# psqlengine = sqlalchemy.create_engine(f"postgresql://"
#                                   f"{os.environ['PSQL_USER']}:"
#                                   f"{os.environ['PSQL_PASSWORD']}"
#                                   f"@localhost/{os.environ['PSQL_DB']}")

# backend = get_backend('postgres://myuser@localhost/mydatabase')
# migrations = read_migrations('path/to/migrations')
#
# with backend.lock():
#
#     # Apply any outstanding migrations
#     backend.apply_migrations(backend.to_apply(migrations))
#
#     # Rollback all migrations
#     backend.rollback_migrations(backend.to_rollback(migrations))

@pytest.fixture()
def empty_inmemory_table_connection():
    # setup inmemory database
    sqlite_engine = sqlalchemy.create_engine('sqlite://')
    connection = sqlite_engine.connect()
    connection.execute("""
    CREATE TABLE blog_user(
        user_id INTEGER PRIMARY KEY,
        name VARCHAR(200),
        surname VARCHAR(200),
        UNIQUE (name,surname)
        );""")
    yield connection
    # teardown
    connection.close()


@pytest.fixture()
def three_users_inmemory_table_connection(empty_inmemory_table_connection):
    # setup
    filled_table_conn = empty_inmemory_table_connection
    filled_table_conn.execute("""
    INSERT INTO blog_user(name, surname)
    VALUES
        ('Renat','Yuldashev'),
        ('Marat','Yuldashev');""")
    return filled_table_conn


def test_get_all_users(three_users_inmemory_table_connection):
    """assuming the test db has more than one row in blog_user table"""
    users = user.get_all_users(three_users_inmemory_table_connection)
    assert len(users) > 0


def test_get_user_1(three_users_inmemory_table_connection):
    # user with this ID should exist
    user_id = 1
    found_user = user.get_user_by_id(user_id, three_users_inmemory_table_connection)
    assert found_user.user_id == user_id


def test_create_new_user(empty_inmemory_table_connection):
    # keyword arguments are used for creation because of Pydantic
    created_user = user.create_user('marat', 'iuldashev', empty_inmemory_table_connection)
    found_user = user.get_user_by_id(created_user.user_id, empty_inmemory_table_connection)
    assert found_user == created_user


def test_create_dublicate_user(empty_inmemory_table_connection):
    # user.User(user_id=0, name='renat', surname='iuldashev')
    with pytest.raises(user.DuplicateUserCreationException):
        user.create_user("Renat", "Yuldashev", empty_inmemory_table_connection)
        assert user.create_user("Renat", "Yuldashev",empty_inmemory_table_connection)

