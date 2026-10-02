from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        return self.session.query(Product).filter(Product.id == product_id).first()

    async def get_by_name(self, name: str) -> Optional[Product]:
        return self.session.query(Product).filter(Product.name == name).first()

    async def search(self, query: str, limit: int = 10) -> List[Product]:
        search_term = f"%{query}%"
        return self.session.query(Product).filter(
            or_(
                Product.name.ilike(search_term),
                Product.brand.ilike(search_term),
                Product.aliases.ilike(search_term)
            )
        ).filter(Product.is_active == True).limit(limit).all()

    async def get_all(self, active_only: bool = True) -> List[Product]:
        query = self.session.query(Product)
        if active_only:
            query = query.filter(Product.is_active == True)
        return query.all()

    async def get_categories(self) -> List[str]:
        return [row[0] for row in self.session.query(Product.category).distinct().all() if row[0]]

    async def create(self, product: ProductCreate) -> Product:
        db_product = Product(
            id=product.id,
            name=product.name,
            brand=product.brand,
            category=product.category,
            subcategory=product.subcategory,
            unit=product.unit,
            pack_size=product.pack_size,
            unit_price=product.unit_price,
            description=product.description,
            aliases=",".join(product.aliases) if product.aliases else None,
            source_product_id=product.source_product_id,
            source_dataset=product.source_dataset,
            is_active=product.is_active
        )
        self.session.add(db_product)
        self.session.flush()
        return db_product

    async def update(self, product_id: str, update: ProductUpdate) -> Optional[Product]:
        product = await self.get_by_id(product_id)
        if not product:
            return None
        for field, value in update.dict(exclude_unset=True).items():
            if field == "aliases" and value is not None:
                setattr(product, field, ",".join(value))
            else:
                setattr(product, field, value)
        self.session.flush()
        return product

    async def delete(self, product_id: str) -> bool:
        product = await self.get_by_id(product_id)
        if not product:
            return False
        self.session.delete(product)
        return True
