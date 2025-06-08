import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from src.models import Wallet

@pytest.fixture
def mock_async_session():
    session = AsyncMock()
    session_maker = MagicMock(return_value=session)
    
    # Настраиваем поведение execute для get_wallet
    session.execute.return_value = MagicMock(
        scalar_one_or_none=AsyncMock()
    )
    return session, session_maker

@pytest.fixture
def sample_wallet():
    return Wallet(
        id="test-wallet-id",
        name="Test Wallet",
        balance=Decimal("100.00")
    )