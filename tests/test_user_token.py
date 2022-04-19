import pytest
import sqlalchemy
from sqlalchemy.future import Connection

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


@pytest.fixture
def three_users_inmemory_table_connection() -> Connection:
    """insert three test users"""
    sqlite_engine = sqlalchemy.create_engine('sqlite://')
    with sqlite_engine.connect() as connection:
        connection: Connection
        connection.execute(CREATE_USER_TABLE)
        connection.execute(ADD_THREE_USERS)
        yield connection


def test_authenticate_user(three_users_inmemory_table_connection):
    token_settings = user_token.TokenSettings(JWT_SECRET_KEY='secret key',
                                              JWT_ENCODE_ALGORITHM='HS256',
                                              JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30)
    user_1_token = user_token.authenticate_user('renatyv', PASSWORDS['renatyv'],
                                                three_users_inmemory_table_connection,
                                                token_settings)
    assert user_token.decode_token_to_user_id(user_1_token, token_settings) == 1
    user_2_token = user_token.authenticate_user('maratyv', PASSWORDS['maratyv'],
                                                three_users_inmemory_table_connection,
                                                token_settings)
    assert user_token.decode_token_to_user_id(user_2_token, token_settings) == 2
