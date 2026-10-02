"""Provider switching with lazy clients and one controlled fallback."""

import logging
from typing import Any, Optional

from app.core.config import settings
from app.schemas.ai import AIParsedOrder, ClarificationOutput
from app.services.ai.errors import AIConfigurationError, AIProviderError
from app.services.ai.gemini_service import GeminiService
from app.services.ai.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class AIProviderRouter:
    def __init__(self) -> None:
        self._services: dict[str, Any] = {}
        self.last_provider: Optional[str] = None

    def _service(self, provider: str):
        provider = provider.lower()
        if provider not in {"gemini", "openai"}:
            raise AIConfigurationError(f"Unsupported AI provider: {provider}")
        if provider not in self._services:
            self._services[provider] = GeminiService() if provider == "gemini" else OpenAIService()
        return self._services[provider]

    @staticmethod
    def _providers(preferred: Optional[str]) -> list[str]:
        first = (preferred or settings.ai_provider).lower()
        second = "openai" if first == "gemini" else "gemini"
        return [first, second]

    async def parse_order(self, text: str, provider: Optional[str] = None) -> AIParsedOrder:
        last_error: Optional[Exception] = None
        for index, selected in enumerate(self._providers(provider)):
            try:
                self.last_provider = selected
                logger.info("[AI] provider=%s operation=order_extraction", selected)
                return await self._service(selected).parse_order(text)
            except AIProviderError as exc:
                last_error = exc
                if provider or index == 1:
                    break
                logger.warning("[AI] provider=%s failed; trying fallback", selected)
        raise last_error or AIProviderError("AI processing is temporarily unavailable")

    async def generate_clarification(
        self, context: str, options: list[str], provider: Optional[str] = None
    ) -> ClarificationOutput:
        last_error: Optional[Exception] = None
        for index, selected in enumerate(self._providers(provider)):
            try:
                self.last_provider = selected
                logger.info("[AI] provider=%s operation=clarification", selected)
                return await self._service(selected).generate_clarification(context, options)
            except AIProviderError as exc:
                last_error = exc
                if provider or index == 1:
                    break
        raise last_error or AIProviderError("AI processing is temporarily unavailable")

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str,
        content_type: Optional[str] = None,
        language: Optional[str] = None,
        context: Optional[str] = None,
    ) -> dict[str, Any]:
        provider = settings.transcription_provider.lower()
        if provider not in {"openai", "gemini"}:
            raise AIConfigurationError(f"Unsupported transcription provider: {provider}")
        logger.info("[TRANSCRIPTION] provider=%s", provider)
        return await self._service(provider).transcribe(
            audio_bytes, filename, content_type=content_type, language=language, context=context
        )
