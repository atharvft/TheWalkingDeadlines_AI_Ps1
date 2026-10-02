"""Lazy OpenAI API integration for transcription and structured extraction."""

import io
import logging
from typing import Any, Optional

from app.core.config import settings
from app.schemas.ai import AIParsedOrder, ClarificationOutput, ai_order_json_schema, clarification_json_schema
from app.services.ai.errors import AIConfigurationError, AIProviderError, AIProviderUnavailable
from app.services.ai.prompts import ORDER_SYSTEM_PROMPT, clarification_prompt

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self) -> None:
        self._client = None

    def _get_client(self):
        if not settings.openai_api_key:
            raise AIConfigurationError("OPENAI_API_KEY is not configured")
        if self._client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError as exc:
                raise AIConfigurationError("OpenAI client dependency is not installed") from exc
            self._client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                timeout=settings.ai_request_timeout_seconds,
                max_retries=0,
            )
        return self._client

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str,
        content_type: Optional[str] = None,
        language: Optional[str] = None,
        context: Optional[str] = None,
    ) -> dict[str, Any]:
        client = self._get_client()
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename or "recording.webm"
        try:
            result = await client.audio.transcriptions.create(
                model=settings.openai_transcription_model,
                file=audio_file,
                language=language,
                prompt=context,
                response_format="json",
            )
        except Exception as exc:
            raise self._safe_provider_error(exc, "transcription") from exc
        text = getattr(result, "text", None) or (result.get("text") if isinstance(result, dict) else "")
        if not text or not text.strip():
            raise AIProviderError("The audio did not contain a usable transcript")
        return {
            "transcript": text.strip(),
            "language": "hi-en",
            "provider": "openai",
            "model": settings.openai_transcription_model,
        }

    async def parse_order(self, text: str) -> AIParsedOrder:
        client = self._get_client()
        try:
            response = await client.responses.create(
                model=settings.openai_text_model,
                input=[
                    {"role": "system", "content": ORDER_SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "hinglish_order",
                        "schema": ai_order_json_schema(),
                        "strict": True,
                    }
                },
            )
            raw = getattr(response, "output_text", "")
            if not raw:
                raise AIProviderError("OpenAI returned an empty order response")
            return AIParsedOrder.parse_raw(raw)
        except AIProviderError:
            raise
        except Exception as exc:
            raise self._safe_provider_error(exc, "order extraction") from exc

    async def generate_clarification(self, context: str, options: list[str]) -> ClarificationOutput:
        client = self._get_client()
        try:
            response = await client.responses.create(
                model=settings.openai_text_model,
                input=[
                    {"role": "system", "content": "You write concise shopkeeper-facing Hinglish clarifications."},
                    {"role": "user", "content": clarification_prompt(context, options)},
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "clarification",
                        "schema": clarification_json_schema(),
                        "strict": True,
                    }
                },
            )
            raw = getattr(response, "output_text", "")
            if not raw:
                raise AIProviderError("OpenAI returned an empty clarification response")
            result = ClarificationOutput.parse_raw(raw)
            result.options = [option for option in result.options if option in options]
            return result
        except AIProviderError:
            raise
        except Exception as exc:
            raise self._safe_provider_error(exc, "clarification generation") from exc

    @staticmethod
    def _safe_provider_error(exc: Exception, operation: str) -> AIProviderError:
        name = exc.__class__.__name__.lower()
        logger.warning("[AI] OpenAI %s failed (%s)", operation, exc.__class__.__name__)
        if "auth" in name or "permission" in name:
            return AIProviderError("OpenAI authentication failed")
        if "rate" in name or "quota" in name:
            return AIProviderUnavailable("OpenAI rate limit or quota reached")
        if "timeout" in name:
            return AIProviderUnavailable("OpenAI request timed out")
        return AIProviderUnavailable("OpenAI is temporarily unavailable")
