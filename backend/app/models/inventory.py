from sqlalchemy import Column, String, Numeric, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base


class Inventory(Base):
    __tablename__ = "inventory"

    product_id = Column(String(64), ForeignKey("products.id"), primary_key=True)
    stock_quantity = Column(Numeric(10, 2), default=0, nullable=False)
    reserved_quantity = Column(Numeric(10, 2), default=0, nullable=False)
    reorder_level = Column(Numeric(10, 2), default=10, nullable=False)
    last_updated = Column(Integer, nullable=True)

    product = relationship("Product")

    def available_quantity(self) -> float:
        return float(self.stock_quantity or 0) - float(self.reserved_quantity or 0)
