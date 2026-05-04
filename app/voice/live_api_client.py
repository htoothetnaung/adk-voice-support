"""Gemini Live API client boundary.

The real network connection is intentionally guarded by config. Offline tests and
evals use `simulate_turn` so the project runs without API keys.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.config import settings
from app.services import SupportAgentRunner


@dataclass
class LiveApiTurn:
    """Simulated Live API response."""

    transcript: str
    text_response: str
    audio_bytes: bytes
    interrupted: bool = False


class GeminiLiveApiClient:
    """Boundary for future Gemini Live API WebSocket calls."""

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        self.model = model or settings.gemini_live_model
        self.api_key = api_key or settings.google_api_key

    @property
    def available(self) -> bool:
        """Return whether a real Live API session can be attempted."""

        return bool(self.api_key and settings.enable_live_api)

    async def connect(self) -> None:
        """Placeholder for a real Gemini Live WebSocket connection."""

        if not self.available:
            raise RuntimeError("Gemini Live API is disabled or GOOGLE_API_KEY is missing.")

    def simulate_turn(self, transcript: str, runner: SupportAgentRunner | None = None) -> LiveApiTurn:
        """Simulate an audio-to-audio turn from a transcript."""

        active_runner = runner or SupportAgentRunner()
        support_response = active_runner.run(transcript)
        return LiveApiTurn(
            transcript=transcript,
            text_response=support_response.final_response,
            audio_bytes=support_response.final_response.encode("utf-8"),
        )

