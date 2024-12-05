import jwt
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


def create_jwt_token(subject: str):
    payload = {
        'sub': subject,
        'exp': settings.TOKEN_EXPIRE
    }
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
