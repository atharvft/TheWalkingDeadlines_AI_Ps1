from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    asr_model: str = "base"
    asr_device: str = "auto"
    nlp_model: str = "gpt-3.5-turbo"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    matching_threshold: float = 0.75
    fuzzy_threshold: float = 60.0
    semantic_threshold: float = 0.5
    ambiguity_threshold: float = 0.75


DEFAULT_CONFIG = ModelConfig()


def get_config() -> ModelConfig:
    return DEFAULT_CONFIG