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

from blog import database
from blog.model import user

# Oauth2 authentification
# token is a relative url. Browser will use it to send login and password
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


class AuthorizationSettings(BaseSettings):
    """ Pydantic will read and validate these parameters from the environment variables"""
    JWT_SECRET_KEY: str
    JWT_ENCODE_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int


# load settings from environment
authorization_settings = AuthorizationSettings()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plaintext_password, hash) -> bool:
    try:
        return pwd_context.verify(plaintext_password, hash)
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
    if not verify_password(password, found_user.password_hash):
        raise PasswordDoesNotMatchException()
    jwt_token_subject = str(found_user.user_info.user_id)
    return create_access_token(data={"sub": jwt_token_subject})


def create_access_token(data: dict) -> str:
    """creates JWT access token, storing data in it.
    :returns JWT access token"""
    to_encode = data.copy()
    expires_delta = timedelta(minutes=authorization_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    logger.debug(f'encoding access token: {data}')
    encoded_jwt = jwt.encode(to_encode, authorization_settings.JWT_SECRET_KEY, algorithm=authorization_settings.JWT_ENCODE_ALGORITHM)
    logger.debug(f"encoded token:{encoded_jwt}")
    return encoded_jwt


def get_current_authenticated_user_id(token: str = Depends(oauth2_scheme)) -> int:
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
        logger.debug(f'token:{token}')
        payload = jwt.decode(token, authorization_settings.JWT_SECRET_KEY, algorithms=[authorization_settings.JWT_ENCODE_ALGORITHM])
        logger.debug(f'payload:{payload}')
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except ExpiredSignatureError:
        logger.debug('signature is expired')
        raise credentials_exception
    except JWTClaimsError:
        logger.debug('If any claim is invalid in any way')
        raise credentials_exception
    except JWTError:
        # JWTError: If .
        # ExpiredSignatureError: If the signature has expired.
        # JWTClaimsError: If any claim is invalid in any way
        logger.debug('the token signature is invalid in any way')
        raise credentials_exception
    return user_id


class Token(BaseModel):
    access_token: str
    token_type: str
