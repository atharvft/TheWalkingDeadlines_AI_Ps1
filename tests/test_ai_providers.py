import pytest

from app.schemas.ai import AIParsedOrder, ai_order_json_schema
from app.services.ai.ai_router import AIProviderRouter
from app.services.ai.errors import AIProviderUnavailable
from app.services.speech.transcription_service import TranscriptionService


def test_provider_schema_requires_language_fields_without_catalog_facts():
    schema = ai_order_json_schema()
    assert schema["required"] == ["items", "delivery"]
    assert "price" not in str(schema).lower()
    parsed = AIParsedOrder.parse_obj({"items": [{"product": "oil"}], "delivery": {}})
    assert parsed.items[0].product == "oil"
    assert parsed.items[0].quantity is None


@pytest.mark.asyncio
async def test_router_uses_configured_provider_and_one_fallback():
    router = AIProviderRouter()
    calls = []

    class FailingGemini:
        async def parse_order(self, text):
            calls.append("gemini")
            raise AIProviderUnavailable("temporary")

    class WorkingOpenAI:
        async def parse_order(self, text):
            calls.append("openai")
            return AIParsedOrder.parse_obj({"items": [{"product": "atta"}], "delivery": {}})

    router._services = {"gemini": FailingGemini(), "openai": WorkingOpenAI()}
    with pytest.raises(AIProviderUnavailable):
        await router.parse_order("atta", provider="gemini")
    assert calls == ["gemini"]

    router._services = {"gemini": FailingGemini(), "openai": WorkingOpenAI()}
    result = await router.parse_order("atta")
    assert result.items[0].product == "atta"
    assert calls[-2:] == ["gemini", "openai"]


@pytest.mark.asyncio
async def test_router_sends_transcription_to_configured_gemini_provider(monkeypatch):
    router = AIProviderRouter()
    calls = []

    class GeminiTranscriber:
        async def transcribe(self, audio_bytes, filename, content_type=None, language=None, context=None):
            calls.append((audio_bytes, filename, content_type, language, context))
            return {
                "transcript": "do kilo atta",
                "language": "hi-en",
                "provider": "gemini",
                "model": "gemini-3.5-transcribe",
            }

    monkeypatch.setattr("app.services.ai.ai_router.settings.transcription_provider", "gemini")
    router._services = {"gemini": GeminiTranscriber()}

    result = await router.transcribe(b"audio", "order.webm", content_type="audio/webm")

    assert result["provider"] == "gemini"
    assert result["model"] == "gemini-3.5-transcribe"
    assert calls == [(b"audio", "order.webm", "audio/webm", None, None)]


@pytest.mark.asyncio
async def test_transcription_service_returns_english_for_hindi_audio_transcript():
    class HindiTranscriptRouter:
        async def transcribe(self, *args, **kwargs):
            return {"transcript": "भैया दो किलो आटा और आधा किलो चीनी देना", "provider": "gemini"}

    result = await TranscriptionService(HindiTranscriptRouter()).transcribe(b"audio", "order.webm", "audio/webm")

    assert result["transcript"] == "2 kg wheat flour and 0.5 kg sugar please"
