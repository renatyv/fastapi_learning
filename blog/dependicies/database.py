from typing import Generator, AsyncGenerator
from pydantic import BaseSettings

import sqlalchemy
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection


class DatabaseSettings(BaseSettings):
    """ Pydantic will read and validate DB connection parameters from the environment variables"""
    PSQL_USER: str
    PSQL_PASSWORD: str
    PSQL_DB: str
    LOG_LEVEL: str
    PSQL_URL: str


db_settings = DatabaseSettings()

# holds connection pool
# put echo=True to log all queries
engine = sqlalchemy.create_engine(f"postgresql://"
                                  f"{db_settings.PSQL_USER}:"
                                  f"{db_settings.PSQL_PASSWORD}"
                                  f"@{db_settings.PSQL_URL}/{db_settings.PSQL_DB}")

# holds connection pool
# put echo=True to log all queries
async_engine = create_async_engine(f"postgresql+asyncpg://"
                                   f"{db_settings.PSQL_USER}:"
                                   f"{db_settings.PSQL_PASSWORD}"
                                   f"@{db_settings.PSQL_URL}/{db_settings.PSQL_DB}")


def get_database_connection() -> Generator:
    """get a connection from pool"""
    connection: Connection = engine.connect()
    try:
        yield connection
    finally:  # executed when response is sent
        connection.close()


async def get_async_db_connection() -> AsyncGenerator:
    """returns async connection. Use .begin to start transaction"""
    connection: AsyncConnection = await async_engine.connect()
    try:
        yield connection
    finally:  # executed when response is sent
        await connection.close()
