from sqlalchemy import Column, String, Numeric, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(64), ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(String(64), ForeignKey("products.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    brand = Column(String(255), nullable=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(32), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    line_total = Column(Numeric(10, 2), nullable=False)
    matched_confidence = Column(Numeric(3, 2), nullable=True)

    order = relationship("Order", back_populates="items")