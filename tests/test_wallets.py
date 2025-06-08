import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.routers import router as wallet_router
from src.services import Walletoperations
from src.schemas import WalletBase, WalletCreate, Operation, Wallet
import decimal
from uuid import uuid4
from unittest.mock import AsyncMock, patch
from decimal import Decimal

app = FastAPI()
app.include_router(wallet_router, prefix="/api/v1/wallets", tags=["wallets"])
client = TestClient(app)


@pytest.fixture
def mock_wallet():
    return {"id": str(uuid4()), "name": "Test Wallet", "balance": Decimal("100.00")}


@pytest.fixture
def valid_operation_data():
    return {"operation_type": "DEPOSIT", "amount": Decimal("50.00")}



@pytest.mark.asyncio
async def test_get_wallet_success(mock_wallet):
    with patch(
        "src.services.Walletoperations.get_wallet", new_callable=AsyncMock
    ) as mock_get:
        wallet_obj = Wallet(**mock_wallet)
        mock_get.return_value = wallet_obj

        response = client.get(
            f"/api/v1/wallets/{mock_wallet['id']}",
            params={"wallet_id": mock_wallet["id"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == mock_wallet["id"]
        assert Decimal(data["balance"]) == mock_wallet["balance"]


@pytest.mark.asyncio
async def test_get_wallet_not_found():
    with patch(
        "src.services.Walletoperations.get_wallet", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = None

        non_existent_id = str(uuid4())
        response = client.get(
            f"/api/v1/wallets/{non_existent_id}", params={"wallet_id": non_existent_id}
        )

        assert response.status_code == 404



@pytest.mark.asyncio
async def test_create_wallet_success():
    wallet_data = {"name": "New Wallet"}

    with patch(
        "src.services.Walletoperations.create_wallet", new_callable=AsyncMock
    ) as mock_create:
        new_wallet = Wallet(id=str(uuid4()), balance=Decimal("0.00"))
        mock_create.return_value = new_wallet

        response = client.post("/api/v1/wallets/create_wallet", json=wallet_data)

        assert response.status_code == 200
        assert "id" in response.json()


@pytest.mark.asyncio
async def test_create_wallet_failure():
    wallet_data = {"name": "New Wallet"}

    with patch(
        "src.services.Walletoperations.create_wallet", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = None

        response = client.post("/api/v1/wallets/create_wallet", json=wallet_data)

        assert response.status_code == 500



@pytest.mark.asyncio
async def test_deposit_operation_success(mock_wallet, valid_operation_data):
    with (
        patch(
            "src.services.Walletoperations.get_wallet", new_callable=AsyncMock
        ) as mock_get,
        patch(
            "src.services.Walletoperations.update_balance", new_callable=AsyncMock
        ) as mock_update,
    ):

        wallet_obj = Wallet(**mock_wallet)
        
        updated_wallet = Wallet(
            id=mock_wallet["id"],
            balance=mock_wallet["balance"] + valid_operation_data["amount"],
        )

        mock_get.return_value = wallet_obj
        mock_update.return_value = updated_wallet

        response = client.post(
            f"/api/v1/wallets/{mock_wallet['id']}/operation",
            json={
                "operation_type": "DEPOSIT",
                "amount": str(valid_operation_data["amount"]),
            },
            params={"wallet_id": mock_wallet["id"]},
        )

        assert response.status_code == 200
        
        assert Decimal(response.json()["balance"]) == Decimal("150.00")


@pytest.mark.asyncio
async def test_withdraw_operation_success(mock_wallet):
    with (
        patch(
            "src.services.Walletoperations.get_wallet", new_callable=AsyncMock
        ) as mock_get,
        patch(
            "src.services.Walletoperations.update_balance", new_callable=AsyncMock
        ) as mock_update,
    ):

        wallet_obj = Wallet(**mock_wallet)
        updated_wallet = Wallet(
            id=mock_wallet["id"], balance=mock_wallet["balance"] - Decimal("30.00")
        )

        mock_get.return_value = wallet_obj
        mock_update.return_value = updated_wallet

        response = client.post(
            f"/api/v1/wallets/{mock_wallet['id']}/operation",
            json={"operation_type": "WITHDRAW", "amount": "30.00"},
            params={"wallet_id": mock_wallet["id"]},
        )

        assert response.status_code == 200
        assert Decimal(response.json()["balance"]) == Decimal("70.00")


@pytest.mark.asyncio
async def test_withdraw_insufficient_funds(mock_wallet):
    with (
        patch(
            "src.services.Walletoperations.get_wallet", new_callable=AsyncMock
        ) as mock_get,
        patch(
            "src.services.Walletoperations.update_balance", new_callable=AsyncMock
        ) as mock_update,
    ):

        wallet_obj = Wallet(**mock_wallet)
        mock_get.return_value = wallet_obj
        mock_update.side_effect = ValueError("Insufficient funds")

        response = client.post(
            f"/api/v1/wallets/{mock_wallet['id']}/operation",
            json={"operation_type": "WITHDRAW", "amount": "150.00"},
            params={"wallet_id": mock_wallet["id"]},
        )

        assert response.status_code == 400


@pytest.mark.asyncio
async def test_invalid_operation_type(mock_wallet):
    response = client.post(
        f"/api/v1/wallets/{mock_wallet['id']}/operation",
        json={"operation_type": "INVALID", "amount": "10.00"},
        params={"wallet_id": mock_wallet["id"]},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_negative_amount_operation(mock_wallet):
    with patch(
        "src.services.Walletoperations.update_balance", new_callable=AsyncMock
    ) as mock_update:
        mock_update.side_effect = ValueError("Amount must be positive")

        response = client.post(
            f"/api/v1/wallets/{mock_wallet['id']}/operation",
            json={"operation_type": "DEPOSIT", "amount": "-10.00"},
            params={"wallet_id": mock_wallet["id"]},
        )

        assert response.status_code == 400
