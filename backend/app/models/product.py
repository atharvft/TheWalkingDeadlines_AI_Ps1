from sqlalchemy import Column, String, Text, Numeric, Boolean
from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(255), nullable=True)
    category = Column(String(128), nullable=True, index=True)
    subcategory = Column(String(128), nullable=True, index=True)
    unit = Column(String(32), nullable=False)
    pack_size = Column(String(64), nullable=True)
    unit_price = Column(Numeric(10, 2), nullable=False)
    description = Column(Text, nullable=True)
    aliases = Column(Text, nullable=True)
    normalized_name = Column(String(255), nullable=True, index=True)
    source_product_id = Column(String(128), nullable=True, index=True)
    source_dataset = Column(String(128), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
