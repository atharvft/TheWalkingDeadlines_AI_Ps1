import io
import wave
import numpy as np
from typing import Tuple


def convert_webm_to_wav(webm_bytes: bytes) -> bytes:
    pass


def resample_audio(audio_data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    pass


def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
    if np.max(np.abs(audio_data)) > 0:
        return audio_data / np.max(np.abs(audio_data))
    return audio_data


def get_audio_duration(audio_bytes: bytes) -> float:
    pass


def split_audio_chunks(audio_data: np.ndarray, chunk_length_sec: float, sample_rate: int) -> list:
    pass