from fastapi import FastAPI, Request
from src.routers import router as wallet_router

app = FastAPI()


app.include_router(
    wallet_router,
    prefix="/api/v1/wallets",
    tags=["wallets"])