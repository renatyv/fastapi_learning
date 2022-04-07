from pydantic import BaseSettings
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from jose.exceptions import JWTClaimsError
from loguru import logger
from pydantic import BaseSettings, BaseModel
from sqlalchemy.future import Connection

from blog.model import user
from blog.model.auth import user_password


class TokenSettings(BaseSettings):
    """ Pydantic will read and validate these parameters from the environment variables"""
    JWT_SECRET_KEY: str
    JWT_ENCODE_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int


class PasswordDoesNotMatchException(Exception):
    pass


def authenticate_user(username: str, password: str, db_connection: Connection, token_settings: TokenSettings) -> str:
    """find user in database and compare password hashes
    :raises UserNotFoundException
    :raises PasswordDoesNotMatchException
    :returns encoded JWT token"""
    found_user = user.get_user_by_username(username=username, db_connection=db_connection)
    if not found_user:
        raise user.UserNotFoundException()
    if not user_password.verify_password(password, found_user.password_hash):
        raise PasswordDoesNotMatchException()
    jwt_token_subject = str(found_user.user_info.user_id)
    return _create_access_token(data={"sub": jwt_token_subject},
                                token_settings=token_settings)


def _create_access_token(data: dict, token_settings: TokenSettings) -> str:
    """creates JWT access token, storing data in it.
    :returns JWT access token"""
    to_encode = data.copy()
    expires_delta = timedelta(minutes=token_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, token_settings.JWT_SECRET_KEY,
                             algorithm=token_settings.JWT_ENCODE_ALGORITHM)
    return encoded_jwt


class BadTokenException(Exception):
    pass


def decode_token_to_user_id(token: str, token_settings: TokenSettings) -> int:
    """decodes user_if from token
    :return user_id
    :raises BadTokenException"""
    bad_token_exception = BadTokenException()
    try:
        payload = jwt.decode(token, token_settings.JWT_SECRET_KEY,
                             algorithms=[token_settings.JWT_ENCODE_ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise bad_token_exception
    except ExpiredSignatureError:
        logger.info('signature is expired')
        raise bad_token_exception
    except JWTClaimsError:
        logger.info('If any claim is invalid in any way')
        raise bad_token_exception
    except JWTError:
        logger.info('the token signature is invalid in any way')
        raise bad_token_exception
    return user_id