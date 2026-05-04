"""Live API session manager."""

from __future__ import annotations

import time
from dataclasses import dataclass

from app.services import SupportAgentRunner
from app.services.adk_runtime import ADKLiveSession, ADKRuntime, adk_runtime
from app.services.interrupt_handler import InterruptHandler, InterruptResult
from app.voice.audio_manager import AudioManager
from app.voice.live_api_client import GeminiLiveApiClient


@dataclass
class VoiceTurnResult:
    """Structured result for a voice turn."""

    approach: str
    transcript: str
    text_response: str
    audio_bytes: bytes
    latency_ms: int
    interrupt: InterruptResult | None = None


class LiveApiSession:
    """Manage a Gemini Live API-style session."""

    def __init__(
        self,
        client: GeminiLiveApiClient | None = None,
        runner: SupportAgentRunner | None = None,
        runtime: ADKRuntime | None = None,
        audio_manager: AudioManager | None = None,
        interrupt_handler: InterruptHandler | None = None,
    ) -> None:
        self.client = client or GeminiLiveApiClient()
        self.runner = runner or SupportAgentRunner()
        self.runtime = runtime or adk_runtime
        self.audio_manager = audio_manager or AudioManager()
        self.interrupt_handler = interrupt_handler or InterruptHandler()

    async def prepare_adk_live_session(
        self,
        user_id: str = "local_user",
        session_id: str | None = None,
    ) -> ADKLiveSession:
        """Prepare official ADK streaming resources for a real Live API session."""

        return await self.runtime.create_live_session(user_id=user_id, session_id=session_id)

    def run_transcript_turn(self, transcript: str, simulate_interrupt: bool = False) -> VoiceTurnResult:
        """Run a transcript through the Live API simulation path."""

        started = time.perf_counter()
        self.interrupt_handler.start_agent_speech()
        turn = self.client.simulate_turn(transcript, self.runner)
        self.audio_manager.output_buffer.append(turn.audio_bytes)
        interrupt = None
        if simulate_interrupt:
            interrupt = self.interrupt_handler.handle_server_interrupt()
            self.audio_manager.clear_playback()
        else:
            self.interrupt_handler.finish_agent_speech()

        return VoiceTurnResult(
            approach="live_api",
            transcript=turn.transcript,
            text_response=turn.text_response,
            audio_bytes=self.audio_manager.output_buffer.read_all(),
            latency_ms=int((time.perf_counter() - started) * 1000),
            interrupt=interrupt,
        )
