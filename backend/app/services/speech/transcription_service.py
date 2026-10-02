"""Input validation around the backend-only OpenAI transcription provider."""

from pathlib import Path
from typing import Optional

from ai.nlp.normalization import hindi_audio_to_english_text
from app.core.config import settings
from app.services.ai.ai_router import AIProviderRouter
from app.services.ai.errors import AIProviderError


class AudioValidationError(ValueError):
    pass


class TranscriptionService:
    allowed_suffixes = {".webm", ".wav", ".mp3", ".m4a", ".mp4", ".mpeg", ".mpga", ".ogg", ".flac", ".aiff"}

    def __init__(self, ai_router: AIProviderRouter) -> None:
        self.ai_router = ai_router

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "recording.webm",
        content_type: Optional[str] = None,
        language: Optional[str] = None,
        context: Optional[str] = None,
    ) -> dict:
        if not audio_bytes:
            raise AudioValidationError("Audio file is empty")
        if len(audio_bytes) > settings.max_audio_bytes:
            raise AudioValidationError("Audio file is too large")
        suffix = Path(filename or "recording.webm").suffix.lower()
        if suffix not in self.allowed_suffixes:
            raise AudioValidationError("Unsupported audio format")
        if content_type and not (content_type.startswith("audio/") or content_type in {"video/webm", "video/mp4"}):
            raise AudioValidationError("File must be an audio recording")
        result = await self.ai_router.transcribe(
            audio_bytes,
            filename=filename or "recording.webm",
            content_type=content_type,
            language=language,
            context=context,
        )
        # This is intentionally provider-neutral. Whether Gemini or OpenAI
        # transcribes the recording, supported Hindi/Hinglish grocery terms
        # are returned to the frontend as English before order parsing starts.
        result["transcript"] = hindi_audio_to_english_text(result.get("transcript", ""))
        return result
