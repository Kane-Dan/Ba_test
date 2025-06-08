from uuid import uuid4
from sqlalchemy import Column, Numeric, Integer, MetaData, String, UUID
from src.database import Base

metadata = MetaData()


class Wallet(Base):
    __tablename__ = "walets"
    id = Column(String, primary_key=True, unique=True)
    balance = Column(Numeric(scale=2), nullable=False, default=0)
    name = Column(String, nullable=False)
