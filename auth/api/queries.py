from sqlmodel import Session, select

from api.schemas import UserInput, User


def create_user(db: Session, user: UserInput) -> User:
    db_user = User.model_validate(user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def read_user(db: Session, username: str) -> User | None:
    query = select(User).where(User.username == username)
    user_in_db = db.exec(query).one_or_none()
    return user_in_db


def update_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
