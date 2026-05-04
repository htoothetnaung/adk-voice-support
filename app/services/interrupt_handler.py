"""Interrupt handling abstractions shared by live and pipeline voice modes."""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class InterruptResult:
    """Result of an interrupt handling action."""

    interrupted: bool
    source: str
    latency_ms: int
    action: str


class InterruptHandler:
    """Track playback state and clear output when user speech interrupts it."""

    def __init__(self) -> None:
        self.is_speaking = False
        self.interrupt_count = 0

    def start_agent_speech(self) -> None:
        """Mark the agent as currently speaking."""

        self.is_speaking = True

    def finish_agent_speech(self) -> None:
        """Mark the agent as no longer speaking."""

        self.is_speaking = False

    def handle_server_interrupt(self, detected_at: float | None = None) -> InterruptResult:
        """Handle a Live API server-side interrupt signal."""

        return self._handle_interrupt("server", detected_at)

    def handle_client_speech_detected(self, detected_at: float | None = None) -> InterruptResult:
        """Handle a client-side VAD interrupt during pipeline playback."""

        if not self.is_speaking:
            return InterruptResult(False, "client", 0, "continue_listening")
        return self._handle_interrupt("client", detected_at)

    def _handle_interrupt(self, source: str, detected_at: float | None) -> InterruptResult:
        started = detected_at or time.perf_counter()
        self.interrupt_count += 1
        self.is_speaking = False
        latency_ms = int((time.perf_counter() - started) * 1000)
        return InterruptResult(True, source, latency_ms, "clear_playback_buffer")

