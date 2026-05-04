"""Simple PCM audio buffer helpers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AudioBuffer:
    """In-memory byte buffer for mocked PCM audio chunks."""

    sample_rate: int
    chunks: list[bytes] = field(default_factory=list)

    def append(self, chunk: bytes) -> None:
        """Append an audio chunk."""

        if chunk:
            self.chunks.append(chunk)

    def read_all(self) -> bytes:
        """Return all audio bytes without clearing the buffer."""

        return b"".join(self.chunks)

    def clear(self) -> None:
        """Clear buffered audio."""

        self.chunks.clear()


class AudioManager:
    """Manage input and output audio buffers."""

    def __init__(self, input_sample_rate: int = 16000, output_sample_rate: int = 24000) -> None:
        self.input_buffer = AudioBuffer(input_sample_rate)
        self.output_buffer = AudioBuffer(output_sample_rate)

    def clear_playback(self) -> None:
        """Clear output playback buffer after an interrupt."""

        self.output_buffer.clear()

