import pytest
import sqlalchemy
from sqlalchemy.future import Connection

from blog.model import post


@pytest.fixture()
def empty_inmemory_table_connection():
    # setup inmemory database
    sqlite_engine = sqlalchemy.create_engine('sqlite://')
    connection = sqlite_engine.connect()
    connection.execute("""
    CREATE TABLE blog_post(
        post_id INTEGER NOT NULL PRIMARY KEY,
        user_id INTEGER,
        title VARCHAR(200),
        body VARCHAR(100000));""")
    yield connection
    # teardown
    connection.close()


@pytest.fixture()
def three_posts_inmemory_table_connection(empty_inmemory_table_connection) -> Connection:
    """Has three posts"""
    filled_table_conn = empty_inmemory_table_connection
    filled_table_conn.execute("""
    INSERT INTO blog_post(post_id, user_id, title, body)
        VALUES (1, 1, 'Migrations with yoyo', 'Actually work'),
               (2, 2, 'Order #1', 'Invade ukraine!'),
               (3, 2, 'Order #2', 'Wtf is going on');""")
    return filled_table_conn


def test_get_post_by_post_id(three_posts_inmemory_table_connection):
    first_post = post.get_post_by_id(1, three_posts_inmemory_table_connection)
    assert first_post.post_id == 1 and first_post.user_id == 1 and first_post.title == 'Migrations with yoyo'


def test_create_new_post(empty_inmemory_table_connection):
    new_post = post.create_post(user_id=1, title='Life is going well',
                                body='For me', db_connection=empty_inmemory_table_connection)
    assert new_post.post_id == 1


def test_update_nonexistent_post(empty_inmemory_table_connection):
    with pytest.raises(post.PostNotFoundException):
        post.update_post(1, 1, 'title', 'body', empty_inmemory_table_connection)


def test_update_post_unauthorized(three_posts_inmemory_table_connection):
    with pytest.raises(post.NotYourPostException):
        post.update_post(caller_user_id=2,
                         post_id=1,
                         title='Updated_title',
                         body='Updated_body',
                         db_connection=three_posts_inmemory_table_connection)


def test_update_post(three_posts_inmemory_table_connection):
    post.update_post(1, 1, 'Updated_title', 'Updated_body', three_posts_inmemory_table_connection)
    actual_post = post.get_post_by_id(1, three_posts_inmemory_table_connection)
    assert actual_post.title == 'Updated_title' and actual_post.body == 'Updated_body'
