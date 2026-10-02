from sqlalchemy import Column, String, Text, Integer, Numeric, Boolean
from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(255), nullable=True)
    category = Column(String(128), nullable=True, index=True)
    unit = Column(String(32), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    description = Column(Text, nullable=True)
    aliases = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)