"""Fallback STT -> support runner -> TTS voice pipeline."""

from __future__ import annotations

import time

from app.services import SupportAgentRunner
from app.services.interrupt_handler import InterruptHandler
from app.voice.audio_manager import AudioManager
from app.voice.live_api_session import VoiceTurnResult
from app.voice.stt import MockSTTProvider
from app.voice.tts import MockTTSProvider
from app.voice.vad import SimpleVAD


class VoicePipelineRunner:
    """Run a voice turn through the fallback pipeline in offline-safe form."""

    def __init__(
        self,
        stt_provider: MockSTTProvider | None = None,
        tts_provider: MockTTSProvider | None = None,
        runner: SupportAgentRunner | None = None,
        vad: SimpleVAD | None = None,
        interrupt_handler: InterruptHandler | None = None,
        audio_manager: AudioManager | None = None,
    ) -> None:
        self.stt_provider = stt_provider or MockSTTProvider()
        self.tts_provider = tts_provider or MockTTSProvider()
        self.runner = runner or SupportAgentRunner()
        self.vad = vad or SimpleVAD()
        self.interrupt_handler = interrupt_handler or InterruptHandler()
        self.audio_manager = audio_manager or AudioManager()

    def run_transcript_turn(self, transcript: str, simulate_interrupt: bool = False) -> VoiceTurnResult:
        """Run one transcript through STT, text runner, and TTS."""

        started = time.perf_counter()
        stt_result = self.stt_provider.transcribe(transcript)
        support_response = self.runner.run(stt_result["transcript"])
        tts_result = self.tts_provider.synthesize(support_response.final_response)
        self.interrupt_handler.start_agent_speech()
        self.audio_manager.output_buffer.append(tts_result["audio_bytes"])

        interrupt = None
        if simulate_interrupt and self.vad.is_speech(b"\x01"):
            interrupt = self.interrupt_handler.handle_client_speech_detected()
            self.audio_manager.clear_playback()
        else:
            self.interrupt_handler.finish_agent_speech()

        return VoiceTurnResult(
            approach="pipeline",
            transcript=stt_result["transcript"],
            text_response=support_response.final_response,
            audio_bytes=self.audio_manager.output_buffer.read_all(),
            latency_ms=int((time.perf_counter() - started) * 1000),
            interrupt=interrupt,
        )

