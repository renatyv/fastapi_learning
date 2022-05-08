import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

import blog.model.auth.user_token as user_token
from blog.model.auth import user_password

CREATE_USER_TABLE = """CREATE TABLE blog_user(
                user_id INTEGER PRIMARY KEY,
                password_hash VARCHAR(300),
                email VARCHAR(254),
                username VARCHAR(100) UNIQUE,
                name VARCHAR(200),
                surname VARCHAR(200));"""

PASSWORDS = {'renatyv': user_password.hash_password('11'),
             'maratyv': user_password.hash_password('22'),
             'putin': user_password.hash_password('33')}

HASHES = {k: user_password.hash_password(password) for k, password in PASSWORDS.items()}

ADD_THREE_USERS = f"""INSERT INTO blog_user(username, email, password_hash, name, surname)
    VALUES
        ('renatyv', 'renatyv@gmail.com', '{HASHES['renatyv']}', 'Renat', 'Yuldashev'),
        ('maratyv', 'maratyv@gmail.com', '{HASHES['maratyv']}', 'Marat', 'Yuldashev'),
        ('putin', 'putin@russia.ru', '{HASHES['putin']}', 'Vladimir', 'Putin');"""


@pytest_asyncio.fixture
async def three_users_connection_async() -> AsyncConnection:
    # create inmemory database
    sqlite_engine = create_async_engine('sqlite+aiosqlite://')
    # creating users table
    async with sqlite_engine.connect() as async_connection:
        async with sqlite_engine.begin():
            await async_connection.execute(text(CREATE_USER_TABLE))
            await async_connection.execute(text(ADD_THREE_USERS))
    # returning new connection
    returned_connection = await sqlite_engine.connect()
    yield returned_connection
    # the following code is executed by pytest after the test using this fixture is executed
    await returned_connection.close()
    await sqlite_engine.dispose()


@pytest.mark.asyncio
async def test_authenticate_user(three_users_connection_async):
    token_settings = user_token.TokenSettings(JWT_SECRET_KEY='secret key',
                                              JWT_ENCODE_ALGORITHM='HS256',
                                              JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30)
    user_1_token = await user_token.authenticate_user('renatyv', PASSWORDS['renatyv'],
                                                      three_users_connection_async,
                                                      token_settings)
    assert user_token.decode_token_to_user_id(user_1_token, token_settings) == 1
    user_2_token = await user_token.authenticate_user('maratyv', PASSWORDS['maratyv'],
                                                      three_users_connection_async,
                                                      token_settings)
    assert user_token.decode_token_to_user_id(user_2_token, token_settings) == 2
