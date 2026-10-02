from sqlalchemy import Column, String, Text, Integer, JSON
from app.db.base import Base


class ConversationState(Base):
    __tablename__ = "conversation_states"

    order_id = Column(String(64), primary_key=True)
    current_step = Column(String(64), nullable=False)
    parsed_data = Column(JSON, nullable=True)
    matched_products = Column(JSON, nullable=True)
    clarification_history = Column(JSON, nullable=True)
    awaiting_question_index = Column(Integer, nullable=True)
    updated_at = Column(Integer, nullable=False)