from fastapi import APIRouter
from app.api.routes import health, transcription, orders, clarification

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(transcription.router, prefix="/transcription", tags=["transcription"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(clarification.router, tags=["clarification"])