
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlmodel import create_engine, Session
from fastapi import Depends

from api.schemas import User
from api.queries import read_user
from core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def get_db():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


async def get_current_user(db: SessionDep, token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get('sub')
        if not username:
            return credentials_exception
    except InvalidTokenError:
        return credentials_exception
    user_in_db = read_user(db, username)
    if not user_in_db:
        return credentials_exception
    if not user_in_db.active:
        raise HTTPException(status_code=400, detail="Token expired")
    return user_in_db


CurrentUser = Annotated[User, Depends(get_current_user)]
