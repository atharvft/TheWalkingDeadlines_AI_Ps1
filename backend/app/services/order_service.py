from typing import Optional
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.services.catalog_service import CatalogService
from app.services.inventory_service import InventoryService
from app.services.clarification_service import ClarificationService
from app.services.billing_service import BillingService
from app.schemas.order import OrderCreate, OrderResponse
from app.schemas.ai import AIProcessingResult
from app.models.order import Order, OrderStatus
from app.core.exceptions import OrderDeskException


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        catalog_service: CatalogService,
        inventory_service: InventoryService,
        clarification_service: ClarificationService,
        billing_service: BillingService
    ):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.catalog_service = catalog_service
        self.inventory_service = inventory_service
        self.clarification_service = clarification_service
        self.billing_service = billing_service

    async def create_order_from_text(self, text: str) -> OrderResponse:
        # TODO: Call AI NLP to parse text
        # TODO: Call matching to match products
        # TODO: Validate inventory
        # TODO: Handle ambiguities
        raise NotImplementedError("Not implemented")

    async def create_order_from_voice(self, audio_data: bytes) -> OrderResponse:
        # TODO: Call AI ASR to transcribe
        # TODO: Process as text order
        raise NotImplementedError("Not implemented")

    async def get_order(self, order_id: str) -> Optional[OrderResponse]:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return None
        return self._to_response(order)

    async def answer_clarification(self, order_id: str, question_index: int, answer: str) -> OrderResponse:
        # TODO: Process clarification answer
        # TODO: Re-validate order
        raise NotImplementedError("Not implemented")

    async def skip_clarification(self, order_id: str, question_index: int) -> OrderResponse:
        # TODO: Skip clarification
        raise NotImplementedError("Not implemented")

    async def confirm_order(self, order_id: str) -> OrderResponse:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderDeskException("Order not found", "ORDER_NOT_FOUND")

        if order.status != OrderStatus.CONFIRMED and order.status != OrderStatus.PENDING:
            raise OrderDeskException("Order cannot be confirmed in current state", "INVALID_ORDER_STATE")

        # Reserve inventory
        await self.inventory_service.reserve_stock(order.items)

        # Calculate bill
        bill = await self.billing_service.calculate_bill(order)

        # Update order
        order.status = OrderStatus.CONFIRMED
        order.subtotal = bill.subtotal
        order.tax = bill.tax
        order.total_amount = bill.total
        order.confirmed_at = int(__import__('time').time())

        await self.order_repo.update(order)
        return self._to_response(order)

    def _to_response(self, order: Order) -> OrderResponse:
        return OrderResponse(
            id=order.id,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            customer_address=order.customer_address,
            status=order.status.value,
            items=[
                type('obj', (object,), {
                    'id': item.id,
                    'product_name': item.product_name,
                    'brand': item.brand,
                    'quantity': float(item.quantity),
                    'unit': item.unit,
                    'unit_price': float(item.unit_price),
                    'line_total': float(item.line_total),
                    'matched_confidence': float(item.matched_confidence) if item.matched_confidence else None
                })()
                for item in order.items
            ],
            subtotal=float(order.subtotal),
            tax=float(order.tax),
            total_amount=float(order.total_amount),
            notes=order.notes,
            created_at=order.created_at,
            updated_at=order.updated_at,
            confirmed_at=order.confirmed_at
        )