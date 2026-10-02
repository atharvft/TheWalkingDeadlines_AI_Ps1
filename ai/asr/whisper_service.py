from typing import Optional
import tempfile
import os


class WhisperService:
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.model = None
        self.device = "cpu"

    def load_model(self):
        pass

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> dict:
        return {
            "text": "[MOCK] Transcribed text from audio",
            "segments": [],
            "language": language or "en"
        }

    def transcribe_from_bytes(self, audio_bytes: bytes, language: Optional[str] = None) -> dict:
        return self.transcribe("", language)