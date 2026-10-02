import os
from typing import Optional


class Settings:
    def __init__(self):
        # Load .env file
        from dotenv import load_dotenv
        load_dotenv()

        self.app_name: str = os.getenv("APP_NAME", "hinglish-order-desk")
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.debug: bool = os.getenv("DEBUG", "true").lower() == "true"

        self.backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
        self.backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))

        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///backend/data/orderdesk.db")

        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        self.ai_provider: str = os.getenv("AI_PROVIDER", "gemini").lower()
        self.transcription_provider: str = os.getenv("TRANSCRIPTION_PROVIDER", "openai").lower()
        self.openai_text_model: str = os.getenv("OPENAI_TEXT_MODEL", "gpt-4o-mini")
        self.openai_transcription_model: str = os.getenv("OPENAI_TRANSCRIPTION_MODEL", "gpt-4o-mini-transcribe")
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.gemini_transcription_model: str = os.getenv("GEMINI_TRANSCRIPTION_MODEL", "gemini-3.5-transcribe")
        self.matching_threshold: float = float(os.getenv("MATCHING_THRESHOLD", "0.75"))

        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.catalog_path: str = os.getenv("CATALOG_PATH", "data/catalog/products.json")
        self.raw_catalog_path: str = os.getenv("RAW_CATALOG_PATH", "data/raw/bigbasket.csv")
        self.max_audio_bytes: int = int(os.getenv("MAX_AUDIO_BYTES", str(25 * 1024 * 1024)))
        self.ai_request_timeout_seconds: float = float(os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "30"))


settings = Settings()
