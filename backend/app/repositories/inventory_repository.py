from typing import Optional
from sqlalchemy.orm import Session
from app.models.inventory import Inventory


class InventoryRepository:
    def __init__(self, session: Session):
        self.session = session

    async def get_by_product_id(self, product_id: str) -> Optional[Inventory]:
        return self.session.query(Inventory).filter(Inventory.product_id == product_id).first()

    async def update(self, inventory: Inventory) -> Inventory:
        self.session.flush()
        return inventory

    async def update_stock(self, product_id: str, quantity: float) -> Inventory:
        inventory = await self.get_by_product_id(product_id)
        if not inventory:
            inventory = Inventory(product_id=product_id, stock_quantity=quantity)
            self.session.add(inventory)
        else:
            inventory.stock_quantity = quantity
        self.session.flush()
        return inventory