from typing import Generator
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator, Field

import sqlalchemy


class DatabaseSettings(BaseSettings):
    """ Pydantic will read and validate DB connection parameters from the environment variables"""
    PSQL_USER: str
    PSQL_PASSWORD: str
    PSQL_DB: str
    LOG_LEVEL: str
    PSQL_URL: str


db_settings = DatabaseSettings()


engine = sqlalchemy.create_engine(f"postgresql://"
                                  f"{db_settings.PSQL_USER}:"
                                  f"{db_settings.PSQL_PASSWORD}"
                                  f"@{db_settings.PSQL_URL}/{db_settings.PSQL_DB}")


def get_database_connection() -> Generator:
    """get a connection from pool"""
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()
