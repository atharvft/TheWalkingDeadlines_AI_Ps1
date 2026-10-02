from typing import List, Optional
from app.repositories.product_repository import ProductRepository
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse


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