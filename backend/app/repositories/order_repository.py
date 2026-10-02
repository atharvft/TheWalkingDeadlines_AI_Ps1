from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.order import Order, OrderItem, OrderStatus
from app.models.conversation_state import ConversationState


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    async def get_by_id(self, order_id: str) -> Optional[Order]:
        return self.session.query(Order).filter(Order.id == order_id).first()

    async def get_by_status(self, status: OrderStatus, limit: int = 50) -> List[Order]:
        return self.session.query(Order).filter(Order.status == status).limit(limit).all()

    async def create(self, order: Order) -> Order:
        self.session.add(order)
        self.session.flush()
        return order

    async def update(self, order: Order) -> Order:
        self.session.flush()
        return order

    async def add_item(self, item: OrderItem) -> OrderItem:
        self.session.add(item)
        self.session.flush()
        return item

    async def get_conversation_state(self, order_id: str) -> Optional[ConversationState]:
        return self.session.query(ConversationState).filter(ConversationState.order_id == order_id).first()

    async def save_conversation_state(self, state: ConversationState) -> ConversationState:
        existing = await self.get_conversation_state(state.order_id)
        if existing:
            for key, value in state.__dict__.items():
                if not key.startswith('_'):
                    setattr(existing, key, value)
            self.session.flush()
            return existing
        else:
            self.session.add(state)
            self.session.flush()
            return state