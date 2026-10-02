from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class Bill:
    subtotal: float
    tax: float
    total: float
    tax_rate: float = 0.18


class BillingService:
    def __init__(self, tax_rate: float = 0.18):
        self.tax_rate = tax_rate

    async def calculate_bill(self, order) -> Bill:
        money = Decimal("0.01")
        subtotal_decimal = sum(
            (Decimal(str(item.quantity)) * Decimal(str(item.unit_price))).quantize(money, rounding=ROUND_HALF_UP)
            for item in order.items
        )
        tax_decimal = (subtotal_decimal * Decimal(str(self.tax_rate))).quantize(money, rounding=ROUND_HALF_UP)
        total_decimal = subtotal_decimal + tax_decimal
        return Bill(subtotal=float(subtotal_decimal), tax=float(tax_decimal), total=float(total_decimal), tax_rate=self.tax_rate)

    async def generate_delivery_note(self, order) -> dict:
        bill = await self.calculate_bill(order)
        return {
            "order_id": order.id,
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "customer_address": order.customer_address,
            "items": [
                {
                    "product_name": item.product_name,
                    "brand": item.brand,
                    "quantity": float(item.quantity),
                    "unit": item.unit,
                    "unit_price": float(item.unit_price),
                    "line_total": float(item.quantity) * float(item.unit_price)
                }
                for item in order.items
            ],
            "subtotal": bill.subtotal,
            "tax": bill.tax,
            "total": bill.total
        }
