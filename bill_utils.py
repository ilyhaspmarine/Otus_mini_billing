from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from bill_db_schema import Wallet as WalletSchema, Transaction as TransactionSchema
from bill_models import WalletReturn
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

async def get_wallet_by_uname(
    uname: str,
    db: AsyncSession
):
    result = await db.execute(select(WalletSchema).filter(WalletSchema.uname == uname))
    return result.scalar_one_or_none()


async def get_balance_delta(
    uname: str,
    later_then: datetime,
    db: AsyncSession
):
    result = await db.execute(
        select(func.sum(TransactionSchema.amount)).where(
            and_(
                TransactionSchema.uname == uname,
                TransactionSchema.datetime > later_then
            )
        )
    )
    total = result.scalar()
    return total if total is not None else Decimal("0")


async def process_new_transaction(
    uname: str,
    transaction_amount: Decimal,
    db: AsyncSession    
):    
    if transaction_amount == 0:
        raise HTTPException(
            status_code = status.HTTP_406_NOT_ACCEPTABLE,
            detail = 'No zero amount transactions please!'
        )

    wallet_state = await get_wallet_by_uname(uname, db)
    
    if wallet_state is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'Billing account not found'
        )

    balance = await get_current_balance(wallet_state, db)

    new_balance = balance + transaction_amount

    if new_balance < 0:
        raise HTTPException(
            status_code = status.HTTP_406_NOT_ACCEPTABLE,
            detail = 'Insufficient funds'
        )        
    
    db_transaction = TransactionSchema(
        id = uuid4(),
        uname = uname,
        amount = transaction_amount,
        datetime = datetime.utcnow()
    )

    db.add(db_transaction)
    try:
        await db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = 'Failed to create transaction'
        )
    
    return WalletReturn(
        uname = uname,
        amount = new_balance
    )

async def get_current_balance(
    wallet_state: WalletSchema,
    db: AsyncSession    
):
    balance_delta = await get_balance_delta(wallet_state.uname, wallet_state.actual_at, db)
    return wallet_state.balance + balance_delta