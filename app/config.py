"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is declared for normal use.
    load_dotenv = None


def _load_env() -> None:
    if load_dotenv is not None:
        load_dotenv()


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    google_api_key: str | None
    adk_model: str
    app_env: str
    log_level: str
    gemini_live_model: str
    gemini_live_api_endpoint: str
    enable_live_api: bool
    stt_provider: str
    tts_provider: str
    deepgram_api_key: str | None
    elevenlabs_api_key: str | None
    audio_input_sample_rate: int
    audio_output_sample_rate: int
    audio_chunk_size_ms: int
    vad_aggressiveness: int


def load_settings() -> Settings:
    """Load settings from `.env` and process environment variables."""

    _load_env()
    return Settings(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        adk_model=os.getenv("ADK_MODEL", "gemini-2.5-flash"),
        app_env=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        gemini_live_model=os.getenv("GEMINI_LIVE_MODEL", "gemini-3.1-flash-live-preview"),
        gemini_live_api_endpoint=os.getenv(
            "GEMINI_LIVE_API_ENDPOINT",
            "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent",
        ),
        enable_live_api=_get_bool("ENABLE_LIVE_API", False),
        stt_provider=os.getenv("STT_PROVIDER", "deepgram"),
        tts_provider=os.getenv("TTS_PROVIDER", "gemini-tts"),
        deepgram_api_key=os.getenv("DEEPGRAM_API_KEY"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
        audio_input_sample_rate=_get_int("AUDIO_INPUT_SAMPLE_RATE", 16000),
        audio_output_sample_rate=_get_int("AUDIO_OUTPUT_SAMPLE_RATE", 24000),
        audio_chunk_size_ms=_get_int("AUDIO_CHUNK_SIZE_MS", 20),
        vad_aggressiveness=_get_int("VAD_AGGRESSIVENESS", 2),
    )


settings = load_settings()

