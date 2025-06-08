from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from src.config import DATABASE_URL_ASYNC
from src.config import DATABASE_URL


Base = declarative_base()


async_engine = create_async_engine(DATABASE_URL_ASYNC, future=True, echo=True)


sync_engine = create_engine(DATABASE_URL, future=True, echo=True)


async_session_maker = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session():
    async with async_session_maker() as session:
        yield session


sync_session_maker = sessionmaker(bind=sync_engine)

