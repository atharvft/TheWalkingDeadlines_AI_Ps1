from fastapi import HTTPException, status


class OrderDeskException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details=None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)


class ProductNotFoundError(OrderDeskException):
    def __init__(self, product_id: str):
        super().__init__(f"Product not found: {product_id}", "PRODUCT_NOT_FOUND")


class InsufficientStockError(OrderDeskException):
    def __init__(self, product_id: str, requested: float, available: float):
        super().__init__(
            f"Insufficient stock for {product_id}: requested {requested}, available {available}",
            "INSUFFICIENT_STOCK"
        )


class AmbiguityError(OrderDeskException):
    def __init__(self, question: str, options: list = None):
        super().__init__(question, "AMBIGUITY_DETECTED")
        self.question = question
        self.options = options or []


class InvalidOrderStateError(OrderDeskException):
    def __init__(self, current_state: str, required_state: str):
        super().__init__(
            f"Invalid order state: {current_state}, required: {required_state}",
            "INVALID_ORDER_STATE"
        )


def http_exception_from_orderdesk(exc: OrderDeskException) -> HTTPException:
    status_codes = {
        "PRODUCT_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "INSUFFICIENT_STOCK": status.HTTP_409_CONFLICT,
        "AMBIGUITY_DETECTED": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "INVALID_ORDER_STATE": status.HTTP_400_BAD_REQUEST,
        "INVALID_ORDER": status.HTTP_400_BAD_REQUEST,
        "QUESTION_NOT_FOUND": status.HTTP_400_BAD_REQUEST,
        "NO_CLARIFICATION": status.HTTP_400_BAD_REQUEST,
        "CLARIFICATION_REQUIRED": status.HTTP_409_CONFLICT,
        "ORDER_NOT_CONFIRMED": status.HTTP_409_CONFLICT,
        "TRANSCRIPTION_FAILED": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "EMPTY_TRANSCRIPT": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "INVALID_CLARIFICATION": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "AI_CONFIGURATION": status.HTTP_503_SERVICE_UNAVAILABLE,
        "AI_UNAVAILABLE": status.HTTP_503_SERVICE_UNAVAILABLE,
        "AUDIO_TOO_LARGE": status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        "UNSUPPORTED_AUDIO": status.HTTP_400_BAD_REQUEST,
    }
    return HTTPException(
        status_code=status_codes.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR),
        detail={"message": exc.message, "code": exc.code, "details": exc.details}
    )
