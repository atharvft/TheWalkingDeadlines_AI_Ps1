from typing import List, Optional
from app.repositories.product_repository import ProductRepository
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
import json


class CatalogService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    async def get_product(self, product_id: str) -> Optional[Product]:
        return await self.product_repo.get_by_id(product_id)

    async def get_product_by_name(self, name: str) -> Optional[Product]:
        return await self.product_repo.get_by_name(name)

    async def search_products(self, query: str, limit: int = 10) -> List[Product]:
        return await self.product_repo.search(query, limit)

    async def get_all_products(self, active_only: bool = True) -> List[Product]:
        return await self.product_repo.get_all(active_only)

    async def create_product(self, product: ProductCreate) -> Product:
        return await self.product_repo.create(product)

    async def update_product(self, product_id: str, update: ProductUpdate) -> Optional[Product]:
        return await self.product_repo.update(product_id, update)

    async def delete_product(self, product_id: str) -> bool:
        return await self.product_repo.delete(product_id)

    async def get_categories(self) -> List[str]:
        return await self.product_repo.get_categories()

    async def get_matching_catalog(self) -> List[dict]:
        products = await self.product_repo.get_all(active_only=True)
        result = []
        for product in products:
            try:
                aliases = json.loads(product.aliases) if product.aliases else []
            except (TypeError, json.JSONDecodeError):
                aliases = [value.strip() for value in (product.aliases or "").split(",") if value.strip()]
            result.append({
                "id": product.id,
                "name": product.name,
                "brand": product.brand,
                "category": product.category,
                "subcategory": getattr(product, "subcategory", None),
                "unit": product.unit,
                "pack_size": getattr(product, "pack_size", None),
                "unit_price": float(product.unit_price),
                "description": product.description,
                "aliases": aliases,
                "is_active": product.is_active,
            })
        return result
