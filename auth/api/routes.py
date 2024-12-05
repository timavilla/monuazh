from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.schemas import Token, UserInput, UserPublic, Message
from api.security import create_jwt_token, hash_password, verify_password
from api.queries import read_user, create_user, update_user
from api.deps import SessionDep, CurrentUser
from core.logger import get_logger

logger = get_logger()


def authenticate_user(db: SessionDep, username: str, password: str) -> bool:
    user_in_db = read_user(db, username)
    if not user_in_db:
        return False
    if not verify_password(password=password, hashed_password=user_in_db.password):
        return False
    return True


router = APIRouter()

@router.post('/register')
def make_user(db: SessionDep, user_request: UserInput) -> UserPublic:
    logger.info(f'Start user {user_request.username} registration')
    user_in_db = read_user(db, user_request.username)
    if user_in_db:
        logger.info(f'User {user_request.username} already exists')
        raise HTTPException(status_code=400, detail='User already exists')
    user_request.password = hash_password(user_request.password)
    user = create_user(db, user_request)
    logger.info(f'Successfully created user {user.username}')
    return user


@router.post('/login')
def login(db: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    logger.info(f'Start user {form_data.username} login')
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.info(f'Login for user {form_data.username} failed: incorrect username or password')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_jwt_token(subject=form_data.username)
    logger.info(f'User {form_data.username} successfully logged in')
    return Token(access_token=token, token_type='bearer')


@router.patch('/user')
def update_password(db: SessionDep, current_user: CurrentUser, password: str) -> Message:
    """
    Change current user password. Unable to change to the same password as current one.
    """
    logger.info(f'Start updating password for user {current_user.username}')
    if verify_password(password=password, hashed_password=current_user.password):
        logger.info(f'Password for user {current_user.username} is not changed')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Password is not changed')


    current_user.password = hash_password(password)
    update_user(db, current_user)
    logger.info(f'Successfully updated password for user {current_user.username}')
    return Message(message='Password updated')


@router.get('/user/me')
def get_me(current_user: CurrentUser) -> UserPublic:
    return current_user
