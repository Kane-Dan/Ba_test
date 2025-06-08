from fastapi import APIRouter, HTTPException
from src.schemas import WalletBase, WalletCreate, Wallet, Operation
from src.services import Walletoperations
from uuid import UUID

router = APIRouter()


@router.post("/create_wallet")
async def create_new_wallet(wallet_data: WalletCreate):
    new_wallet = await Walletoperations.create_wallet(wallet_data)
    if new_wallet is None:
        raise HTTPException(status_code=500, detail="Wallet not found")
    return new_wallet


@router.get("/{wallet_UUID}")
async def get_wallet(wallet_id: str):
    wallet = await Walletoperations.get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@router.post("/{wallet_UUID}/operation")
async def perform_operation(
    wallet_id: str,
    operation: Operation,
):
    if operation.operation_type not in ["DEPOSIT", "WITHDRAW"]:
        raise HTTPException(status_code=400, detail="Invalid operation type")

    try:
        updated_wallet = await Walletoperations.update_balance(wallet_id, operation)
        return {
            "balance": float(updated_wallet.balance)
        }  
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
