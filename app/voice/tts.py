"""Text-to-speech provider boundaries."""

from __future__ import annotations


class MockTTSProvider:
    """Deterministic TTS provider used for offline tests and evals."""

    name = "mock"

    def synthesize(self, text: str) -> dict:
        """Return encoded text as deterministic mock audio bytes."""

        return {"provider": self.name, "audio_bytes": text.encode("utf-8"), "duration_sec": max(len(text) / 18.0, 0.1)}


class GeminiTTSProvider:
    """Gemini TTS provider placeholder with explicit dependency guard."""

    name = "gemini-tts"

    def synthesize(self, text: str) -> dict:
        """Raise until real Gemini TTS is wired for audio output."""

        del text
        raise RuntimeError("Gemini TTS requires provider configuration and is not used in offline mode.")

