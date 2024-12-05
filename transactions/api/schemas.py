from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field


class Message(SQLModel):
    message: str


class TransactionStatus(str, Enum):
    succeed = 'succeed'
    failed = 'failed'


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(index=True)
    password: str
    balance: int = 0
    active: bool = True


class Transaction(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    amount: int
    date: datetime
    status: TransactionStatus
    sender_user_id: UUID = Field(foreign_key='user.id')
    recepient_user_id: UUID = Field(foreign_key='user.id')


class TransactionsParams(SQLModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    date_from: datetime | None = None
    date_to: datetime | None = None
    status: TransactionStatus | None = None


class Transfer(SQLModel):
    username: str
    amount: int = Field(gt=0)
