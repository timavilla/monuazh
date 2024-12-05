from typing import Annotated
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, status

from api.schemas import Transaction, TransactionsParams, TransactionStatus, Transfer, Message
from api.deps import CurrentUser, SessionDep
from api.queries import read_user, update_user, get_user_transactions, perform_transfer, create_transaction
from core.logger import get_logger, get_logger_with_adapter

logger = get_logger()

router = APIRouter()


@router.post('/transfer')
async def send_money(db: SessionDep, current_user: CurrentUser, transfer: Transfer) -> Message:
    """
    Transfer money from current user balance to recipient balance. Can not transfer more, than current balance.
    """
    transfer_log = get_logger_with_adapter(logger, str(uuid4()))
    transfer_log.info(f'Starting transfer. Sender: {current_user.username}, Recipient: {transfer.username}, Amount: {transfer.amount}')

    recipient = read_user(db, username=transfer.username)
    if not recipient:
        transfer_log.info(f'Recipient: {transfer.username} does not exist')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid recipient username')
    if recipient.id == current_user.id:
        transfer_log.info(f'Sender and recipient are the same user. Username: {transfer.username}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Can not perform transfer to yourself')

    def make_transaction(status: TransactionStatus):
        return Transaction(amount=transfer.amount, date=datetime.now(), status=status, sender_user_id=current_user.id, recepient_user_id=recipient.id)
    try:
        perform_transfer(db, logger, sender_user=current_user, recipient_user=recipient, amount=transfer.amount)
    except HTTPException:
        transaction = make_transaction(TransactionStatus.failed)
        create_transaction(db, transaction)
        transfer_log.info(f'Transfer aborted due to incorrect query, transaction.id={str(transaction.id)}')
        raise
    except Exception as e:
        transaction = make_transaction(TransactionStatus.failed)
        create_transaction(db, transaction)
        transfer_log.info(f'Transfer aborted due to an internal error. transaction.id={str(transaction.id)}\nError: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Transaction failed\n{e}')
    transaction = make_transaction(TransactionStatus.succeed)
    create_transaction(db, transaction)
    transfer_log.info(f'Transfer success! New balance: {current_user.balance}')
    return Message(message=f'Transfer success! New balance: {current_user.balance}')


@router.get('/balance')
async def get_balance(current_user: CurrentUser) -> int:
    return current_user.balance


@router.patch('/balance')
async def update_balance(db: SessionDep, current_user: CurrentUser, amount: int) -> Message:
    """
    Add amount to current user balance. Amount can be negative number, as long as it doesnt make balance negative.
    """
    logger.info(f'Start updating user {current_user.username} balance')
    if current_user.balance + amount < 0:
        logger.info(f'Insufficient funds. Balance: {current_user.balance}, {amount=}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Insufficient funds')
    current_user.balance = current_user.balance + amount
    update_user(db, current_user)
    logger.info(f'User {current_user.username} balance was changed succesfully. New balance: {current_user.balance}')
    return Message(message=f'Balance was changed succesfully')


@router.get('/transactions')
async def get_transactions(db: SessionDep, current_user: CurrentUser, params: Annotated[TransactionsParams, Query()]) -> list[Transaction]:
    """
    Show all current user transactions
    """
    if params.date_from and params.date_to and params.date_from > params.date_to:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect dates: date_from is later than date_to')
    transactions = get_user_transactions(db, current_user, params)
    return transactions
