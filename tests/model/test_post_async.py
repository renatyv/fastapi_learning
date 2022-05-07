import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection

from blog.model import post

CREATE_POST_TABLE = """
    CREATE TABLE blog_post(
        post_id INTEGER NOT NULL PRIMARY KEY,
        user_id INTEGER,
        title VARCHAR(200),
        body VARCHAR(100000));"""


@pytest_asyncio.fixture
async def empty_inmemory_table_connection():
    # setup inmemory database
    sqlite_engine = create_async_engine('sqlite+aiosqlite://')
    # creating users table
    async with sqlite_engine.connect() as async_connection:
        async with sqlite_engine.begin():
            await async_connection.execute(text(CREATE_POST_TABLE))
    # returning new connection
    returned_connection = await sqlite_engine.connect()
    yield returned_connection
    # the following code is executed by pytest after the test using this fixture is executed
    await returned_connection.close()
    await sqlite_engine.dispose()


@pytest_asyncio.fixture
async def three_posts_inmemory_table_connection(empty_inmemory_table_connection) -> AsyncConnection:
    """Has three posts"""
    async with empty_inmemory_table_connection.begin():
        await empty_inmemory_table_connection.execute(text("""
            INSERT INTO blog_post(post_id, user_id, title, body)
                VALUES (1, 1, 'Migrations with yoyo', 'Actually work'),
                       (2, 2, 'Order #1', 'Invade ukraine!'),
                       (3, 2, 'Order #2', 'Wtf is going on');"""))
    return empty_inmemory_table_connection


@pytest.mark.asyncio
async def test_get_all_posts(three_posts_inmemory_table_connection):
    posts = await post.get_all_posts_async(three_posts_inmemory_table_connection)
    assert len(posts) == 3
    assert posts[2].user_id == 2 and posts[2].title == 'Order #2'
