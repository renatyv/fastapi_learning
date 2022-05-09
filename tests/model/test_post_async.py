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
async def empty_inmemory_table_connection() -> AsyncConnection:
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
async def test_get_post_by_post_id_async(three_posts_inmemory_table_connection: AsyncConnection):
    first_post = await post.get_post_by_id_async(1, three_posts_inmemory_table_connection)
    assert first_post.post_id == 1 and first_post.user_id == 1 and first_post.title == 'Migrations with yoyo'


@pytest.mark.asyncio
async def test_get_all_posts(three_posts_inmemory_table_connection: AsyncConnection):
    posts = await post.get_all_posts_async(three_posts_inmemory_table_connection)
    assert len(posts) == 3
    assert posts[2].user_id == 2 and posts[2].title == 'Order #2'


@pytest.mark.asyncio
async def test_delete_nonexistent_post(empty_inmemory_table_connection: AsyncConnection):
    """delete post by id"""
    with pytest.raises(post.PostNotFoundException):
        await post.delete_post_async(caller_user_id=1, post_id=0, db_connection=empty_inmemory_table_connection)


@pytest.mark.asyncio
async def test_delete_user(three_posts_inmemory_table_connection: AsyncConnection):
    await post.delete_post_async(caller_user_id=1, post_id=1, db_connection=three_posts_inmemory_table_connection)
    deleted_post = await post.get_post_by_id_async(1, three_posts_inmemory_table_connection)
    assert deleted_post is None


@pytest.mark.asyncio
async def test_delete_unauthorized_user(three_posts_inmemory_table_connection: AsyncConnection):
    with pytest.raises(post.NotYourPostException):
        await post.delete_post_async(caller_user_id=2, post_id=1, db_connection=three_posts_inmemory_table_connection)


@pytest.mark.asyncio
async def test_update_nonexistent_post(empty_inmemory_table_connection):
    with pytest.raises(post.PostNotFoundException):
        await post.update_post(1, 1, 'title', 'body', empty_inmemory_table_connection)


@pytest.mark.asyncio
async def test_update_post_unauthorized(three_posts_inmemory_table_connection):
    with pytest.raises(post.NotYourPostException):
        await post.update_post(caller_user_id=2,
                               post_id=1,
                               title='Updated_title',
                               body='Updated_body',
                               db_connection=three_posts_inmemory_table_connection)


@pytest.mark.asyncio
async def test_update_post(three_posts_inmemory_table_connection):
    await post.update_post(1, 1, 'Updated_title', 'Updated_body', three_posts_inmemory_table_connection)
    actual_post = await post.get_post_by_id_async(1, three_posts_inmemory_table_connection)
    assert actual_post.title == 'Updated_title' and actual_post.body == 'Updated_body'


@pytest.mark.asyncio
async def test_create_new_post(empty_inmemory_table_connection):
    new_post = await post.create_post(user_id=1, title='Life is going well',
                                      body='For me', db_connection=empty_inmemory_table_connection)
    assert new_post.post_id == 1
