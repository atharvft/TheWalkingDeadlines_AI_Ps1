from dataclasses import dataclass
from typing import List
from app.models.order import OrderItem


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
        subtotal = sum(float(item.quantity) * float(item.unit_price) for item in order.items)
        tax = subtotal * self.tax_rate
        total = subtotal + tax
        return Bill(subtotal=subtotal, tax=tax, total=total, tax_rate=self.tax_rate)

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