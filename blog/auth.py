from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import status
from jose import jwt, JWTError, ExpiredSignatureError
from jose.exceptions import JWTClaimsError
from loguru import logger
from passlib.context import CryptContext

from pydantic import BaseSettings, BaseModel
from sqlalchemy.future import Connection

from blog.model import user


class AuthorizationSettings(BaseSettings):
    """ Pydantic will read and validate these parameters from the environment variables"""
    JWT_SECRET_KEY: str
    JWT_ENCODE_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    URL_PREFIX_FOR_V1_API: str


# load settings from environment
__authorization_settings = AuthorizationSettings()

# Oauth2 authentification
__oauth2_scheme = OAuth2PasswordBearer(tokenUrl=__authorization_settings.URL_PREFIX_FOR_V1_API+"/token")

__pwd_context = CryptContext(schemes=["md5_crypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return __pwd_context.hash(password)


def _verify_password(plaintext_password, hash) -> bool:
    try:
        return __pwd_context.verify(plaintext_password, hash)
    except Exception as e:
        logger.error(e)
        return False


class PasswordDoesNotMatchException(Exception):
    pass


def authenticate_user(username: str, password: str, db_connection: Connection) -> str:
    """find user in database and compare password hashes
    :raises UserNotFoundException
    :raises PasswordDoesNotMatchException
    :returns encoded JWT token"""
    found_user = user.get_user_by_username(username=username, db_connection=db_connection)
    if not found_user:
        raise user.UserNotFoundException()
    if not _verify_password(password, found_user.password_hash):
        raise PasswordDoesNotMatchException()
    jwt_token_subject = str(found_user.user_info.user_id)
    return _create_access_token(data={"sub": jwt_token_subject})


def _create_access_token(data: dict) -> str:
    """creates JWT access token, storing data in it.
    :returns JWT access token"""
    to_encode = data.copy()
    expires_delta = timedelta(minutes=__authorization_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, __authorization_settings.JWT_SECRET_KEY,
                             algorithm=__authorization_settings.JWT_ENCODE_ALGORITHM)
    return encoded_jwt


def get_current_authenticated_user_id(token: str = Depends(__oauth2_scheme)) -> int:
    """finds current user using OAuth2 token
    :returns user.User object if authentification is successfull
    :raises user.UserNotFoundException
    :raises HTTPException if authorization went wrong"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, __authorization_settings.JWT_SECRET_KEY,
                             algorithms=[__authorization_settings.JWT_ENCODE_ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except ExpiredSignatureError:
        logger.info('signature is expired')
        raise credentials_exception
    except JWTClaimsError:
        logger.info('If any claim is invalid in any way')
        raise credentials_exception
    except JWTError:
        logger.info('the token signature is invalid in any way')
        raise credentials_exception
    return user_id
