from pydantic import BaseModel, validator
from decimal import Decimal


class WalletBase(BaseModel):
    id: str


class WalletCreate(BaseModel):
    name: str


class Operation(BaseModel):
    operation_type: str
    amount: Decimal


class Wallet(WalletBase):
    balance: Decimal
