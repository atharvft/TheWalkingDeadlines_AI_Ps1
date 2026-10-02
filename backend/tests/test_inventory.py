import pytest
from app.models.inventory import Inventory


class TestInventory:
    def test_inventory_creation(self):
        inv = Inventory(
            product_id="prod-1",
            stock_quantity=100.0,
            reserved_quantity=10.0,
            reorder_level=20.0
        )
        assert inv.product_id == "prod-1"
        assert float(inv.stock_quantity) == 100.0
        assert float(inv.available_quantity()) == 90.0

    def test_available_quantity(self):
        inv = Inventory(product_id="prod-1", stock_quantity=50.0, reserved_quantity=5.0)
        assert float(inv.stock_quantity) - float(inv.reserved_quantity) == 45.0