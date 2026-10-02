from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.dependencies import get_order_service
from app.services.ai.errors import AIProviderError
from app.services.order_service import OrderService
from app.services.speech.transcription_service import AudioValidationError

router = APIRouter()


class TranscriptionResponse(BaseModel):
    success: bool = True
    transcript: str
    language: str = "hi-en"
    provider: str
    model: Optional[str] = None


def _transcription_error(exc: AIProviderError) -> tuple[str, str]:
    message = str(exc).lower()
    if "quota" in message or "rate limit" in message:
        return (
            "The configured transcription provider has reached its rate limit or quota. Try again shortly or update its billing/quota.",
            "TRANSCRIPTION_QUOTA",
        )
    if "authentication" in message or "api key" in message or "not configured" in message:
        return (
            "The transcription API key is missing or invalid. Check the backend .env configuration and restart the backend.",
            "TRANSCRIPTION_AUTH",
        )
    if "model" in message and "unavailable" in message:
        return (
            "The configured transcription model is unavailable for this API project. Check GEMINI_TRANSCRIPTION_MODEL.",
            "TRANSCRIPTION_MODEL",
        )
    if "timed out" in message or "could not connect" in message:
        return (
            "The transcription provider could not be reached. Check your internet connection and try again.",
            "TRANSCRIPTION_NETWORK",
        )
    return ("Unable to transcribe audio. Please try again.", "TRANSCRIPTION_FAILED")


@router.post("/transcribe", response_model=TranscriptionResponse)
@router.post("/transcription", response_model=TranscriptionResponse, include_in_schema=False)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None),
    service: OrderService = Depends(get_order_service),
):
    try:
        data = await audio.read()
        result = await service.transcription_service.transcribe(
            data,
            filename=audio.filename or "recording.webm",
            content_type=audio.content_type,
            language=language,
        )
        return {"success": True, **result}
    except AudioValidationError as exc:
        raise HTTPException(status_code=400, detail={"message": str(exc), "code": "UNSUPPORTED_AUDIO"}) from exc
    except AIProviderError as exc:
        message, code = _transcription_error(exc)
        raise HTTPException(
            status_code=503,
            detail={
                "message": message,
                "code": code,
            },
        ) from exc
