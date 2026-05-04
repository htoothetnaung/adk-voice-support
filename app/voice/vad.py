"""Simple voice activity detection helpers."""

from __future__ import annotations


class SimpleVAD:
    """Detect speech when a chunk contains non-silent bytes."""

    def __init__(self, aggressiveness: int = 2) -> None:
        self.aggressiveness = max(0, min(3, aggressiveness))

    def is_speech(self, chunk: bytes) -> bool:
        """Return whether a chunk contains speech-like signal."""

        return any(byte != 0 for byte in chunk)

