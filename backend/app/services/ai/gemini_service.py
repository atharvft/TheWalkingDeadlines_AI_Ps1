"""Gemini REST integration without a model loaded in the backend process."""

import logging
from typing import Any, Optional

import httpx

from app.core.config import settings
from app.schemas.ai import AIParsedOrder, ClarificationOutput, ai_order_json_schema, clarification_json_schema
from app.services.ai.errors import AIConfigurationError, AIProviderError, AIProviderUnavailable
from app.services.ai.prompts import ORDER_SYSTEM_PROMPT, clarification_prompt

logger = logging.getLogger(__name__)

# Bias recognition toward terms that exist in the grocery transaction flow.
# These are hints only; catalog matching remains the source of product truth.
HINGLISH_GROCERY_VOCABULARY = [
    "bhaiya", "atta", "aashirvaad", "amul", "butter", "fortune", "sunflower oil",
    "mustard oil", "sugar", "cheeni", "shakkar", "rice", "chawal", "dal", "tel",
    "namak", "doodh", "dahi", "maggi", "parle g", "aadha kilo", "paav kilo",
    "dedh kilo", "sawa kilo", "dhai kilo", "kal subah", "ghar pe bhej dena",
]


class GeminiService:
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    files_endpoint = "https://generativelanguage.googleapis.com/upload/v1beta/files"
    interactions_endpoint = "https://generativelanguage.googleapis.com/v1beta/interactions"

    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise AIConfigurationError("GEMINI_API_KEY is not configured")

    async def _generate(self, prompt: str, schema: dict[str, Any]) -> str:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
                "responseJsonSchema": schema,
            },
        }
        try:
            async with httpx.AsyncClient(timeout=settings.ai_request_timeout_seconds) as client:
                response = await client.post(
                    self.endpoint.format(model=settings.gemini_model),
                    headers={"x-goog-api-key": settings.gemini_api_key},
                    json=payload,
                )
            if response.status_code >= 400:
                logger.warning("[AI] Gemini request failed with status %s", response.status_code)
                if response.status_code in {401, 403}:
                    raise AIProviderError("Gemini authentication failed")
                if response.status_code == 429:
                    raise AIProviderUnavailable("Gemini rate limit or quota reached")
                raise AIProviderUnavailable("Gemini is temporarily unavailable")
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except AIProviderError:
            raise
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            logger.warning("[AI] Gemini network failure (%s)", exc.__class__.__name__)
            raise AIProviderUnavailable("Gemini request timed out or could not connect") from exc
        except (KeyError, IndexError, ValueError) as exc:
            raise AIProviderError("Gemini returned an invalid response") from exc
        except Exception as exc:
            logger.warning("[AI] Gemini request failed (%s)", exc.__class__.__name__)
            raise AIProviderUnavailable("Gemini is temporarily unavailable") from exc

    async def parse_order(self, text: str) -> AIParsedOrder:
        raw = await self._generate(
            f"{ORDER_SYSTEM_PROMPT}\nCustomer message:\n{text}",
            ai_order_json_schema(),
        )
        try:
            return AIParsedOrder.parse_raw(raw)
        except ValueError as exc:
            raise AIProviderError("Gemini returned malformed order data") from exc

    async def generate_clarification(self, context: str, options: list[str]) -> ClarificationOutput:
        raw = await self._generate(clarification_prompt(context, options), clarification_json_schema())
        try:
            result = ClarificationOutput.parse_raw(raw)
        except ValueError as exc:
            raise AIProviderError("Gemini returned malformed clarification data") from exc
        result.options = [option for option in result.options if option in options]
        return result

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str,
        content_type: Optional[str] = None,
        language: Optional[str] = None,
        context: Optional[str] = None,
    ) -> dict[str, Any]:
        """Upload a short recording, transcribe it, then remove the temporary Gemini file."""
        mime_type = content_type or self._mime_type_for(filename)
        file_name: Optional[str] = None
        try:
            async with httpx.AsyncClient(timeout=settings.ai_request_timeout_seconds) as client:
                upload_url = await self._start_resumable_upload(client, filename, mime_type, len(audio_bytes))
                uploaded = await self._finish_resumable_upload(client, upload_url, audio_bytes, mime_type)
                file_name = uploaded.get("name")
                file_uri = uploaded.get("uri")
                if not file_uri:
                    raise AIProviderError("Gemini did not return an uploaded audio file")

                # An empty list enables Gemini's automatic language detection
                # and Hindi/English code-switching. Custom vocabulary grounds
                # short shopkeeper voice notes in supported grocery terms.
                transcription_config: dict[str, Any] = {
                    "language_codes": [],
                    "custom_vocabulary": HINGLISH_GROCERY_VOCABULARY,
                }
                if language in {"hi-IN", "en-IN"}:
                    transcription_config["language_codes"] = [language]
                payload = {
                    "model": settings.gemini_transcription_model,
                    "input": [{"type": "audio", "uri": file_uri, "mime_type": uploaded.get("mimeType") or mime_type}],
                    "generation_config": {"transcription_config": transcription_config},
                }
                response = await client.post(
                    self.interactions_endpoint,
                    headers={"x-goog-api-key": settings.gemini_api_key},
                    json=payload,
                )
                self._raise_for_provider_status(response, "transcription")
                transcript = self._extract_text(response.json())
                if not transcript:
                    raise AIProviderError("Gemini returned an empty transcript")
                return {
                    "transcript": transcript,
                    "language": language or "hi-en",
                    "provider": "gemini",
                    "model": settings.gemini_transcription_model,
                }
        except AIProviderError:
            raise
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            logger.warning("[TRANSCRIPTION] Gemini network failure (%s)", exc.__class__.__name__)
            raise AIProviderUnavailable("Gemini transcription timed out or could not connect") from exc
        except (TypeError, ValueError) as exc:
            logger.warning("[TRANSCRIPTION] Gemini returned an invalid response (%s)", exc.__class__.__name__)
            raise AIProviderError("Gemini returned an invalid transcription response") from exc
        except Exception as exc:
            logger.warning("[TRANSCRIPTION] Gemini failed (%s)", exc.__class__.__name__)
            raise AIProviderUnavailable("Gemini transcription is temporarily unavailable") from exc
        finally:
            if file_name:
                await self._delete_uploaded_file(file_name)

    async def _start_resumable_upload(
        self, client: httpx.AsyncClient, filename: str, mime_type: str, content_length: int
    ) -> str:
        response = await client.post(
            self.files_endpoint,
            headers={
                "x-goog-api-key": settings.gemini_api_key,
                "X-Goog-Upload-Protocol": "resumable",
                "X-Goog-Upload-Command": "start",
                "X-Goog-Upload-Header-Content-Length": str(content_length),
                "X-Goog-Upload-Header-Content-Type": mime_type,
                "Content-Type": "application/json",
            },
            json={"file": {"display_name": filename}},
        )
        self._raise_for_provider_status(response, "audio upload")
        upload_url = response.headers.get("x-goog-upload-url")
        if not upload_url:
            raise AIProviderError("Gemini did not provide an audio upload URL")
        return upload_url

    async def _finish_resumable_upload(
        self, client: httpx.AsyncClient, upload_url: str, audio_bytes: bytes, mime_type: str
    ) -> dict[str, Any]:
        response = await client.post(
            upload_url,
            headers={
                "X-Goog-Upload-Command": "upload, finalize",
                "X-Goog-Upload-Offset": "0",
                "Content-Type": mime_type,
            },
            content=audio_bytes,
        )
        self._raise_for_provider_status(response, "audio upload")
        data = response.json()
        uploaded = data.get("file", data)
        if not isinstance(uploaded, dict):
            raise AIProviderError("Gemini returned an invalid uploaded audio file")
        return uploaded

    async def _delete_uploaded_file(self, file_name: str) -> None:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.delete(
                    f"https://generativelanguage.googleapis.com/v1beta/{file_name}",
                    headers={"x-goog-api-key": settings.gemini_api_key},
                )
            if response.status_code >= 400:
                logger.warning("[TRANSCRIPTION] Gemini temporary-file cleanup failed with status %s", response.status_code)
        except Exception as exc:
            logger.warning("[TRANSCRIPTION] Gemini temporary-file cleanup failed (%s)", exc.__class__.__name__)

    @staticmethod
    def _mime_type_for(filename: str) -> str:
        suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        return {
            "webm": "audio/webm",
            "wav": "audio/wav",
            "mp3": "audio/mpeg",
            "m4a": "audio/mp4",
            "mp4": "audio/mp4",
            "ogg": "audio/ogg",
            "flac": "audio/flac",
            "aiff": "audio/aiff",
        }.get(suffix, "application/octet-stream")

    @staticmethod
    def _extract_text(value: Any) -> str:
        if isinstance(value, dict):
            for key in ("output_text", "outputText", "transcript", "text"):
                candidate = value.get(key)
                if isinstance(candidate, str) and candidate.strip():
                    return candidate.strip()
            for candidate in value.values():
                text = GeminiService._extract_text(candidate)
                if text:
                    return text
        if isinstance(value, list):
            for candidate in value:
                text = GeminiService._extract_text(candidate)
                if text:
                    return text
        return ""

    @staticmethod
    def _raise_for_provider_status(response: httpx.Response, operation: str) -> None:
        if response.status_code < 400:
            return
        logger.warning("[AI] Gemini %s failed with status %s", operation, response.status_code)
        if response.status_code in {401, 403}:
            raise AIProviderError("Gemini authentication failed")
        if response.status_code == 404:
            raise AIProviderUnavailable("Gemini transcription model is unavailable")
        if response.status_code == 429:
            raise AIProviderUnavailable("Gemini rate limit or quota reached")
        raise AIProviderUnavailable("Gemini is temporarily unavailable")
