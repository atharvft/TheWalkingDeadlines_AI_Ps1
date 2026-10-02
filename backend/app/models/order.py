from sqlalchemy import Column, String, Text, Numeric, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    CONFIRMED = "confirmed"
    AMBIGUOUS = "ambiguous"
    REJECTED = "rejected"
    COMPLETED = "completed"


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(64), primary_key=True)
    customer_name = Column(String(255), nullable=True)
    customer_phone = Column(String(32), nullable=True)
    customer_address = Column(Text, nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    subtotal = Column(Numeric(10, 2), default=0, nullable=False)
    tax = Column(Numeric(10, 2), default=0, nullable=False)
    total_amount = Column(Numeric(10, 2), default=0, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=False)
    confirmed_at = Column(Integer, nullable=True)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")