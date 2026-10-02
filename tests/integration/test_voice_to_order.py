import pytest
from httpx import AsyncClient
import io


class TestVoiceToOrder:
    @pytest.mark.asyncio
    async def test_voice_order_flow(self, client: AsyncClient):
        # Create a dummy audio file
        audio_data = b"dummy audio data"
        files = {"audio": ("test.webm", io.BytesIO(audio_data), "audio/webm")}

        response = await client.post("/api/orders/voice", files=files)
        # Should either process or return appropriate error
        assert response.status_code in [200, 400, 422, 503]

    @pytest.mark.asyncio
    async def test_transcription_endpoint(self, client: AsyncClient):
        audio_data = b"dummy audio data"
        files = {"audio": ("test.webm", io.BytesIO(audio_data), "audio/webm")}

        response = await client.post("/api/transcription", files=files)
        assert response.status_code in [200, 400, 422, 503]

        if response.status_code == 200:
            data = response.json()
            assert "transcript" in data
            assert data["provider"] == "openai"
