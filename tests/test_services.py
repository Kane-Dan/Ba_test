import pytest
from unittest.mock import patch, AsyncMock
from decimal import Decimal
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from src.services import Walletoperations
from src.schemas import Operation, WalletCreate
from src.models import Wallet

@pytest.mark.asyncio
async def test_get_wallet_found(mock_async_session, sample_wallet):
    session, session_maker = mock_async_session
    session.execute.return_value.scalar_one_or_none.return_value = sample_wallet
    
    with patch("src.services.async_session_maker", session_maker):
        result = await Walletoperations.get_wallet(sample_wallet.id)
    
    assert result == sample_wallet
    session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_wallet_not_found(mock_async_session):
    session, session_maker = mock_async_session
    session.execute.return_value.scalar_one_or_none.return_value = None
    
    with patch("src.services.async_session_maker", session_maker):
        result = await Walletoperations.get_wallet("non-existent-id")
    
    assert result is None

@pytest.mark.asyncio
async def test_update_balance_deposit(mock_async_session, sample_wallet):
    session, session_maker = mock_async_session
    operation = Operation(operation_type="DEPOSIT", amount=Decimal("50.00"))
    
    with patch("src.services.async_session_maker", session_maker), \
         patch("src.services.Walletoperations.get_wallet", AsyncMock(return_value=sample_wallet)):
        
        updated_wallet = await Walletoperations.update_balance(sample_wallet.id, operation)
    
    assert updated_wallet.balance == Decimal("150.00")
    session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_balance_withdraw_ok(mock_async_session, sample_wallet):
    session, session_maker = mock_async_session
    operation = Operation(operation_type="WITHDRAW", amount=Decimal("30.00"))
    
    with patch("src.services.async_session_maker", session_maker), \
         patch("src.services.Walletoperations.get_wallet", AsyncMock(return_value=sample_wallet)):
        
        updated_wallet = await Walletoperations.update_balance(sample_wallet.id, operation)
    
    assert updated_wallet.balance == Decimal("70.00")
    session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_balance_withdraw_insufficient_funds(mock_async_session, sample_wallet):
    session, session_maker = mock_async_session
    operation = Operation(operation_type="WITHDRAW", amount=Decimal("150.00"))
    
    with patch("src.services.async_session_maker", session_maker), \
         patch("src.services.Walletoperations.get_wallet", AsyncMock(return_value=sample_wallet)):
        
        with pytest.raises(ValueError, match="Insufficient funds"):
            await Walletoperations.update_balance(sample_wallet.id, operation)
    
    session.commit.assert_not_called()

@pytest.mark.asyncio
async def test_create_wallet_success(mock_async_session):
    session, session_maker = mock_async_session
    wallet_data = WalletCreate(name="New Wallet")
    test_uuid = "123e4567-e89b-12d3-a456-426614174000"
    
    with patch("src.services.async_session_maker", session_maker), \
         patch("src.services.uuid.uuid4", return_value=test_uuid):
        
        new_wallet = await Walletoperations.create_wallet(wallet_data)
    
    assert new_wallet.id == test_uuid
    assert new_wallet.name == "New Wallet"
    assert new_wallet.balance == Decimal("0.00")
    session.add.assert_called_once()
    session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_wallet_db_error(mock_async_session):
    session, session_maker = mock_async_session
    session.commit.side_effect = SQLAlchemyError("DB Error")
    wallet_data = WalletCreate(name="New Wallet")
    
    with patch("src.services.async_session_maker", session_maker):
        with pytest.raises(SQLAlchemyError):
            await Walletoperations.create_wallet(wallet_data)
    
    session.rollback.assert_called_once()