from typing import List, Optional
from app.repositories.inventory_repository import InventoryRepository
from app.models.inventory import Inventory
from app.models.order_item import OrderItem
from app.core.exceptions import InsufficientStockError


class InventoryService:
    def __init__(self, inventory_repo: InventoryRepository):
        self.inventory_repo = inventory_repo

    async def get_stock(self, product_id: str) -> Optional[Inventory]:
        return await self.inventory_repo.get_by_product_id(product_id)

    async def get_available_quantity(self, product_id: str) -> float:
        inventory = await self.inventory_repo.get_by_product_id(product_id)
        if not inventory:
            return 0.0
        return float(inventory.stock_quantity) - float(inventory.reserved_quantity)

    async def check_availability(self, product_id: str, quantity: float) -> bool:
        available = await self.get_available_quantity(product_id)
        return available >= quantity

    async def validate_order_items(self, items: List[OrderItem]) -> List[dict]:
        issues = []
        for item in items:
            available = await self.get_available_quantity(item.product_id)
            if available < float(item.quantity):
                issues.append({
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "requested": float(item.quantity),
                    "available": available
                })
        return issues

    async def reserve_stock(self, items: List[OrderItem]) -> None:
        for item in items:
            inventory = await self.inventory_repo.get_by_product_id(item.product_id)
            if not inventory:
                raise InsufficientStockError(item.product_id, float(item.quantity), 0)

            available = float(inventory.stock_quantity) - float(inventory.reserved_quantity)
            if available < float(item.quantity):
                raise InsufficientStockError(item.product_id, float(item.quantity), available)

            inventory.reserved_quantity = float(inventory.reserved_quantity) + float(item.quantity)
            await self.inventory_repo.update(inventory)

    async def release_stock(self, items: List[OrderItem]) -> None:
        for item in items:
            inventory = await self.inventory_repo.get_by_product_id(item.product_id)
            if inventory:
                inventory.reserved_quantity = max(0, float(inventory.reserved_quantity) - float(item.quantity))
                await self.inventory_repo.update(inventory)

    async def fulfill_order(self, items: List[OrderItem]) -> None:
        for item in items:
            inventory = await self.inventory_repo.get_by_product_id(item.product_id)
            if inventory:
                inventory.stock_quantity = float(inventory.stock_quantity) - float(item.quantity)
                inventory.reserved_quantity = max(0, float(inventory.reserved_quantity) - float(item.quantity))
                await self.inventory_repo.update(inventory)

    async def update_stock(self, product_id: str, quantity: float) -> Inventory:
        return await self.inventory_repo.update_stock(product_id, quantity)
