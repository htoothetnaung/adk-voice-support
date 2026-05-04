"""Speech-to-text provider boundaries."""

from __future__ import annotations


class MockSTTProvider:
    """Transcript provider used by offline voice tests and evals."""

    name = "mock"

    def transcribe(self, audio_input: bytes | str, expected_transcript: str | None = None) -> dict:
        """Return a transcript from supplied text or expected transcript."""

        if expected_transcript is not None:
            transcript = expected_transcript
        elif isinstance(audio_input, str):
            transcript = audio_input
        else:
            transcript = ""
        return {"provider": self.name, "transcript": transcript, "confidence": 1.0 if transcript else 0.0}


class DeepgramSTTProvider:
    """Deepgram provider placeholder with explicit dependency guard."""

    name = "deepgram"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    def transcribe(self, audio_input: bytes | str, expected_transcript: str | None = None) -> dict:
        """Raise until the real Deepgram streaming integration is configured."""

        del audio_input, expected_transcript
        raise RuntimeError("Deepgram STT requires deepgram-sdk configuration and a real audio stream.")

