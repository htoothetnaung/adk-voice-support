"""Voice-specific intent detection."""

from __future__ import annotations

import re

from app.services.intent_detector import IntentDetector


class VoiceIntentDetector:
    """Normalize spoken transcripts before using the text detector."""

    DISFLUENCIES = {"um", "uh", "like", "you know", "sort of", "kind of"}

    def __init__(self, text_detector: IntentDetector | None = None) -> None:
        self.text_detector = text_detector or IntentDetector()

    def normalize(self, transcript: str) -> str:
        """Remove common voice disfluencies from a transcript."""

        normalized = transcript.lower()
        for filler in self.DISFLUENCIES:
            normalized = re.sub(rf"\b{re.escape(filler)}\b", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized)
        normalized = re.sub(r"^[\s,.;:!?-]+", "", normalized)
        return normalized.strip()

    def detect(self, transcript: str, context: list[dict] | None = None) -> dict:
        """Classify a voice transcript."""

        normalized = self.normalize(transcript)
        result = self.text_detector.detect(normalized, context)
        result["method"] = "voice_transcript"
        result["raw_text"] = transcript
        result["normalized_text"] = normalized
        return result
