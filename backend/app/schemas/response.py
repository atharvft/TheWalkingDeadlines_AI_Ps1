from pydantic import BaseModel
from typing import Optional, Any


class ErrorResponse(BaseModel):
    message: str
    code: str
    details: Optional[Any] = None


class SuccessResponse(BaseModel):
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int