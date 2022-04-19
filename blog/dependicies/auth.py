import os

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.future import Connection
from loguru import logger
from starlette import status

from blog.dependicies import database
import blog.model.user as user
import blog.model.auth.user_password
import blog.model.auth.user_token as user_token

# Oauth2 authentication from FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=os.environ['URL_PREFIX_FOR_V1_API'] + "/token")

# load settings from environment
token_settings = blog.model.auth.user_token.TokenSettings()


def get_current_authenticated_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """finds current user using OAuth2 token
    :returns user_id
    :raises HTTPException if authorization went wrong"""
    try:
        return blog.model.auth.user_token.decode_token_to_user_id(token, token_settings)
    except blog.model.auth.user_token.BadTokenException:
        logger.info('Smth wrong with token {}', token)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": "Bearer"})


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


def generate_JWT_token_from_login_pass(form_data: OAuth2PasswordRequestForm = Depends(),
                                       db_connection: Connection = Depends(database.get_database_connection)) -> Token:
    try:
        return Token(access_token=user_token.authenticate_user(form_data.username,
                                                               form_data.password,
                                                               db_connection,
                                                               token_settings))
    except (user.UserNotFoundException, user_token.PasswordDoesNotMatchException):
        logger.info('Failed authentication for username:{}', form_data.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='wrong username or password')
