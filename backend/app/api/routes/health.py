from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "hinglish-order-desk",
        "transcription_provider": settings.transcription_provider,
        "transcription_model": (
            settings.gemini_transcription_model
            if settings.transcription_provider == "gemini"
            else settings.openai_transcription_model
        ),
    }
