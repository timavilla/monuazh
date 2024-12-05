from logging import Logger

from fastapi import HTTPException, status
from sqlmodel import Session, select, or_

from api.schemas import User, Transaction, TransactionsParams


def read_user(db: Session, username: str) -> User | None:
    query = select(User).where(User.username == username)
    user_in_db = db.exec(query).one_or_none()
    return user_in_db


def update_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_transactions(db: Session, user: User, params: TransactionsParams) -> list[Transaction]:
    query = select(Transaction).where(or_(Transaction.sender_user_id == user.id, Transaction.recepient_user_id == user.id))
    if params.date_from:
        query = query.where(Transaction.date >= params.date_from)
    if params.date_to:
        query = query.where(Transaction.date <= params.date_to)
    if params.status:
        query = query.where(Transaction.status == params.status)
    query = query.offset(params.offset).limit(params.limit)
    transactions = db.exec(query).all()
    return transactions


def perform_transfer(db: Session, logger: Logger, *, sender_user: User, recipient_user: User, amount: int) -> None:
    recipient_query = select(User).where(User.id == recipient_user.id).with_for_update()
    recipient = db.exec(recipient_query).one_or_none()

    if not recipient:
        logger.info(f'Recipient {recipient_user.username} was deleted')
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Recipient was deleted')

    sender_query = select(User).where(User.id == sender_user.id).with_for_update()
    sender = db.exec(sender_query).one()

    if sender.balance < amount:
        logger.info(f'Insufficient funds. Balance: {sender.balance}, {amount=}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='insufficient funds')

    sender.balance -= amount
    recipient.balance += amount

    db.add(sender)
    db.add(recipient)
    db.commit()
    db.refresh(sender)
    db.refresh(recipient)


def create_transaction(db: Session, transaction: Transaction) -> Transaction:
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction
