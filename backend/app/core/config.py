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

        self.asr_model: str = os.getenv("ASR_MODEL", "whisper-base")
        self.nlp_model: str = os.getenv("NLP_MODEL", "hindi-english-mixed")
        self.matching_threshold: float = float(os.getenv("MATCHING_THRESHOLD", "0.75"))

        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()