import pytest
from app.services.billing_service import BillingService
from app.models.order import Order, OrderItem, OrderStatus


class TestBilling:
    @pytest.fixture
    def billing_service(self):
        return BillingService(tax_rate=0.18)

    @pytest.fixture
    def sample_order(self):
        order = Order(
            id="test-1",
            status=OrderStatus.CONFIRMED,
            created_at=1234567890,
            updated_at=1234567890
        )
        order.items = [
            OrderItem(
                id=1,
                order_id="test-1",
                product_id="prod-1",
                product_name="Onions",
                quantity=2.0,
                unit="kg",
                unit_price=40.0,
                line_total=80.0
            ),
            OrderItem(
                id=2,
                order_id="test-1",
                product_id="prod-2",
                product_name="Milk",
                quantity=1.0,
                unit="litre",
                unit_price=60.0,
                line_total=60.0
            )
        ]
        return order

    @pytest.mark.asyncio
    async def test_calculate_bill(self, billing_service, sample_order):
        bill = await billing_service.calculate_bill(sample_order)
        assert bill.subtotal == 140.0
        assert bill.tax == 25.2
        assert bill.total == 165.2