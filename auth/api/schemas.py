from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class Token(SQLModel):
    access_token: str
    token_type: str


class UserInput(SQLModel):
    username: str
    password: str


class UserPublic(SQLModel):
    username: str


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(index=True)
    password: str
    balance: int = 0
    active: bool = True


class Message(SQLModel):
    message: str
