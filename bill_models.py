from pydantic import BaseModel, Field
from decimal import Decimal

class Uname(BaseModel):
    uname: str = Field(..., min_length=1, max_length=100)

class Amount(BaseModel):
    amount: Decimal = Field(..., max_digits = 15, decimal_places= 2)



class WalletBase(Uname):
    pass

class WalletCreate(WalletBase):
    pass

class WalletReturn(WalletBase, Amount):
    pass

    class Config:
        from_attributes = True



class TransactionBase(Uname, Amount):
    pass

class TransactionCreate(TransactionBase):
    pass

class TransactionReturn(TransactionBase):
    id: str = Field()

    class Config:
        from_attributes = True