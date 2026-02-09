from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()


class Wallet(Base):
    __tablename__ = 'wallets'

    # Uname (первичный ключ, уникальное имя пользователя-владельца кошелька)
    username = Column(String(100), primary_key=True, unique=True, nullable=False)

    # Balance (баланс, число со знаком и фиксированной точностью 2 знака после запятой)
    balance = Column(Numeric(precision=15, scale=2), nullable=False)

    # Actual_at (метка даты и времени, на которые актуален баланс)
    actual_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Transaction(Base):
    __tablename__ = 'transactions'

    # ID (уникальный ID транзакции, UUID)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # Uname (внешний ключ к таблице кошельков)
    username = Column(String(100), ForeignKey('wallets.username'), nullable=False)

    # Amount (число со знаком и фиксированной точностью 2 знака после запятой)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)

    # Datetime (метка даты-времени, когда произведена транзакция)
    datetime = Column(DateTime, nullable=False, default=datetime.utcnow)