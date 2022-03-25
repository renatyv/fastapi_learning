from typing import Generator

import sqlalchemy
from loguru import logger
import os

REQUIRED_ENV_VARIABLES = ['PSQL_URL','PSQL_USER', 'PSQL_PASSWORD', 'PSQL_DB', 'LOG_LEVEL']

for env_var in REQUIRED_ENV_VARIABLES:
    if env_var not in os.environ:
        logger.error(f"Environment variable {env_var} is not set")


logger.info("psql url:"+f"postgresql://"
                        f"{os.environ['PSQL_USER']}:"
                        f"PSQL_PASSWORD"
                        f"@{os.environ['PSQL_URL']}/{os.environ['PSQL_DB']}")


engine = sqlalchemy.create_engine(f"postgresql://"
                                  f"{os.environ['PSQL_USER']}:"
                                  f"{os.environ['PSQL_PASSWORD']}"
                                  f"@{os.environ['PSQL_URL']}/{os.environ['PSQL_DB']}")


def get_database_connection() -> Generator:
    connection = engine.connect() # get a connection from pool
    try:
        yield connection
    finally:
        connection.close()
