from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from prometheus_fastapi_instrumentator import Instrumentator
from datetime import datetime
import bill_utils as utils
from bill_db_schema import Wallet as WalletSchema
from bill_db import _get_db
from bill_models import WalletCreate, WalletReturn, TransactionCreate, TransactionReturn


app = FastAPI(title="Billing Service", version="1.0.0")


@app.get('/health', summary='HealthCheck EndPoint', tags=['Health Check'])
def healthcheck():
    return {'status': 'OK'}


@app.post('/register', summary = 'Create Wallet for User', tags = ['Wallet'], response_model = WalletReturn, status_code = status.HTTP_201_CREATED)
async def wallet_create_new(
    wallet: WalletCreate,
    db = Depends(_get_db)
):
    db_wallet = WalletSchema(
        username = wallet.username,
        balance = 0,
        actual_at = datetime.utcnow()
    )
    db.add(db_wallet)
    try:
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'User already exists')
    return WalletReturn (
        username = db_wallet.username,
        amount = db_wallet.balance
    )


@app.post('/transaction', summary = 'Create new transaction', tags = ['Wallet', 'Transactions'], response_model = TransactionReturn, status_code = status.HTTP_201_CREATED)
async def transaction_create(
    transaction: TransactionCreate,
    db = Depends(_get_db)
):
    result = await utils.process_new_transaction(transaction.username, transaction.amount, db)
    return result


@app.get('/wallet/{req_uname}', summary = 'Get current balance', tags = ['Wallet'], response_model = WalletReturn, status_code = status.HTTP_200_OK)
async def get_wallet_balance(
    req_uname: str,
    db = Depends(_get_db)
):
    wallet_state = await utils.get_wallet_by_username(req_uname, db)
    
    if wallet_state is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'Billing account not found'
        )

    balance = await utils.get_current_balance(wallet_state, db)
    
    return WalletReturn(
        username = wallet_state.username,
        amount = balance
    )
