import pytest
from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate


class TestOrders:
    def test_order_creation(self):
        order = Order(
            id="test-1",
            customer_name="Test Customer",
            customer_phone="9876543210",
            status=OrderStatus.PENDING,
            created_at=1234567890,
            updated_at=1234567890
        )
        assert order.id == "test-1"
        assert order.status == OrderStatus.PENDING

    def test_order_status_enum(self):
        assert OrderStatus.PENDING.value == "pending"
        assert OrderStatus.CONFIRMED.value == "confirmed"
        assert OrderStatus.AMBIGUOUS.value == "ambiguous"