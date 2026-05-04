"""ADK runtime helpers aligned with the official streaming lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from uuid import uuid4

from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents.root_agent import root_agent


APP_NAME = "voice-support-adk-lab"


@dataclass(frozen=True)
class ADKSessionIds:
    """Application-defined identifiers for one ADK session."""

    user_id: str = "local_user"
    session_id: str = field(default_factory=lambda: f"session_{uuid4().hex}")
    app_name: str = APP_NAME


@dataclass
class ADKLiveSession:
    """Session-specific resources for one bidirectional streaming session."""

    ids: ADKSessionIds
    run_config: RunConfig
    live_request_queue: LiveRequestQueue
    closed: bool = False

    def close(self) -> None:
        """Close the queue exactly once."""

        if not self.closed:
            self.live_request_queue.close()
            self.closed = True


class ADKRuntime:
    """Reusable ADK runtime infrastructure.

    Official ADK streaming guidance keeps `Agent`, `SessionService`, and
    `Runner` reusable, while `RunConfig` and `LiveRequestQueue` are created per
    streaming session. This class encodes that lifecycle boundary.
    """

    def __init__(
        self,
        app_name: str = APP_NAME,
        session_service: InMemorySessionService | None = None,
        runner: Runner | None = None,
    ) -> None:
        self.app_name = app_name
        self.session_service = session_service or InMemorySessionService()
        self.runner = runner or Runner(
            app_name=app_name,
            agent=root_agent,
            session_service=self.session_service,
        )

    async def get_or_create_session(self, ids: ADKSessionIds) -> object:
        """Return an existing ADK session or create one if missing."""

        session = await self.session_service.get_session(
            app_name=ids.app_name,
            user_id=ids.user_id,
            session_id=ids.session_id,
        )
        if session:
            return session
        return await self.session_service.create_session(
            app_name=ids.app_name,
            user_id=ids.user_id,
            session_id=ids.session_id,
            state={"created_by": "voice-support-adk-lab"},
        )

    def build_run_config(
        self,
        *,
        streaming_mode: StreamingMode = StreamingMode.BIDI,
        response_modalities: list[str] | None = None,
        enable_transcription: bool = True,
        enable_session_resumption: bool = True,
    ) -> RunConfig:
        """Create session-specific streaming configuration."""

        kwargs = {
            "streaming_mode": streaming_mode,
            "response_modalities": response_modalities or ["AUDIO"],
        }
        if enable_transcription:
            kwargs["input_audio_transcription"] = types.AudioTranscriptionConfig()
            kwargs["output_audio_transcription"] = types.AudioTranscriptionConfig()
        if enable_session_resumption:
            kwargs["session_resumption"] = types.SessionResumptionConfig()
        return RunConfig(**kwargs)

    async def create_live_session(
        self,
        *,
        user_id: str = "local_user",
        session_id: str | None = None,
        run_config: RunConfig | None = None,
    ) -> ADKLiveSession:
        """Create the per-session resources needed before `runner.run_live()`."""

        ids = ADKSessionIds(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id or f"session_{uuid4().hex}",
        )
        await self.get_or_create_session(ids)
        return ADKLiveSession(
            ids=ids,
            run_config=run_config or self.build_run_config(),
            live_request_queue=LiveRequestQueue(),
        )

    def send_text(self, live_session: ADKLiveSession, text: str) -> None:
        """Send text content upstream through this session's request queue."""

        content = types.Content(parts=[types.Part(text=text)])
        live_session.live_request_queue.send_content(content)

    def send_audio(self, live_session: ADKLiveSession, audio_data: bytes, sample_rate: int = 16000) -> None:
        """Send PCM audio upstream through this session's request queue."""

        audio_blob = types.Blob(mime_type=f"audio/pcm;rate={sample_rate}", data=audio_data)
        live_session.live_request_queue.send_realtime(audio_blob)

    async def iter_live_events(self, live_session: ADKLiveSession) -> AsyncIterator[object]:
        """Yield downstream ADK events for a live session."""

        async for event in self.runner.run_live(
            user_id=live_session.ids.user_id,
            session_id=live_session.ids.session_id,
            live_request_queue=live_session.live_request_queue,
            run_config=live_session.run_config,
        ):
            yield event

    @staticmethod
    def serialize_event(event: object) -> str:
        """Serialize an ADK event for WebSocket/SSE delivery."""

        if hasattr(event, "model_dump_json"):
            return event.model_dump_json(exclude_none=True, by_alias=True)
        return str(event)


adk_runtime = ADKRuntime()

