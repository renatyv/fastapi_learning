import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine
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


@pytest_asyncio.fixture
async def empty_inmemory_table_connection_async() -> AsyncConnection:
    """
    :return  AsyncConnection
    """
    # create inmemory database
    sqlite_engine = create_async_engine('sqlite+aiosqlite://')
    # creating users table
    async with sqlite_engine.connect() as async_connection:
        async with sqlite_engine.begin():
            await async_connection.execute(text(CREATE_USER_TABLE))
    # returning new connection
    returned_connection = await sqlite_engine.connect()
    yield returned_connection
    # the following code is executed by pytest after the test using this fixture is executed
    await returned_connection.close()
    await sqlite_engine.dispose()


@pytest_asyncio.fixture
async def three_users_inmemory_table_connection_async(empty_inmemory_table_connection_async) -> AsyncConnection:
    """insert three test users"""
    async with empty_inmemory_table_connection_async.begin():
        await empty_inmemory_table_connection_async.execute(text(ADD_THREE_USERS))
    # not empty anymore
    return empty_inmemory_table_connection_async


@pytest.mark.asyncio
async def test_all_users_async(three_users_inmemory_table_connection_async):
    users = await user.get_all_users_async(three_users_inmemory_table_connection_async)
    assert len(users) == 3
