from loguru import logger
from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["md5_crypt"], deprecated="auto")

class NullInPusswordException(Exception):
    pass


def hash_password(password: str) -> str:
    """raises """
    if '\x00' in password:
        raise NullInPusswordException()
    return _pwd_context.hash(password)


def verify_password(plaintext_password: str, correct_password_hash: str) -> bool:
    """returns True if password's hash mathches."""
    try:
        return _pwd_context.verify(plaintext_password, correct_password_hash)
    except Exception as e:
        logger.error(e)
        return False

