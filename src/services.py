import uuid
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from src.models import Wallet
from src.database import async_session_maker 
from src.schemas import Operation,WalletCreate,WalletBase
from fastapi import HTTPException

class Walletoperations:

    async def get_wallet(wallet_id:str):
        async with async_session_maker() as session:
            result = await session.execute(
            select(Wallet).where(Wallet.id == wallet_id))
        return result.scalar_one_or_none()
    
    async def update_balance(wallet_id:str,operation: Operation):
        async with async_session_maker() as session:
            try:
                wallet = await Walletoperations.get_wallet(wallet_id)
                if not wallet:
                    raise HTTPException(status_code=404, detail="Wallet not found")
                if operation.operation_type == "DEPOSIT":
                    wallet.balance += operation.amount
                elif operation.operation_type == "WITHDRAW":
                    if wallet.balance < operation.amount:
                        raise ValueError("Insufficient funds")
                    wallet.balance -= operation.amount
                session.add(wallet)
                await session.commit()
                await session.refresh(wallet) 
                return wallet   
            except SQLAlchemyError as e:
                await session.rollback()
                raise
                

    async def create_wallet(wallet_data:WalletCreate):
        async with async_session_maker() as session:
            try:
                new_wallet = Wallet(
                    id=str(uuid.uuid4()),
                    name=wallet_data.name,
                    balance=0.00
                )
                session.add(new_wallet)
                await session.commit()
                await session.refresh(new_wallet)
                return new_wallet
            except SQLAlchemyError as e:
                await session.rollback()
                raise