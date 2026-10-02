from pydantic import BaseModel
from typing import Optional, List


class ProductBase(BaseModel):
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    unit: str
    pack_size: Optional[str] = None
    unit_price: float
    description: Optional[str] = None
    aliases: Optional[List[str]] = None
    source_product_id: Optional[str] = None
    source_dataset: Optional[str] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    id: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    unit: Optional[str] = None
    pack_size: Optional[str] = None
    unit_price: Optional[float] = None
    description: Optional[str] = None
    aliases: Optional[List[str]] = None
    source_product_id: Optional[str] = None
    source_dataset: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: str

    class Config:
        orm_mode = True


class ProductMatch(BaseModel):
    product: ProductResponse
    confidence: float
    match_type: str
