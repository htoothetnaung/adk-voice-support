import asyncio

from google.adk.agents.run_config import StreamingMode

from app.services.adk_runtime import ADKRuntime, ADKSessionIds
from app.voice.live_api_session import LiveApiSession


def test_get_or_create_session_is_idempotent() -> None:
    async def run() -> None:
        runtime = ADKRuntime()
        ids = ADKSessionIds(user_id="tester", session_id="same_session", app_name=runtime.app_name)

        first = await runtime.get_or_create_session(ids)
        second = await runtime.get_or_create_session(ids)

        assert first.id == second.id
        assert first.user_id == "tester"

    asyncio.run(run())


def test_create_live_session_uses_fresh_queue_per_session() -> None:
    async def run() -> None:
        runtime = ADKRuntime()

        first = await runtime.create_live_session(user_id="tester", session_id="one")
        second = await runtime.create_live_session(user_id="tester", session_id="two")

        assert first.ids.session_id == "one"
        assert second.ids.session_id == "two"
        assert first.live_request_queue is not second.live_request_queue
        first.close()
        second.close()
        assert first.closed is True
        assert second.closed is True

    asyncio.run(run())


def test_build_run_config_defaults_to_bidi_audio_with_transcription() -> None:
    run_config = ADKRuntime().build_run_config()

    assert run_config.streaming_mode == StreamingMode.BIDI
    assert run_config.response_modalities == ["AUDIO"]
    assert run_config.input_audio_transcription is not None
    assert run_config.output_audio_transcription is not None
    assert run_config.session_resumption is not None


def test_send_text_and_audio_to_live_queue() -> None:
    async def run() -> None:
        runtime = ADKRuntime()
        live_session = await runtime.create_live_session(user_id="tester", session_id="queue_session")

        runtime.send_text(live_session, "hello")
        runtime.send_audio(live_session, b"\x01\x02", sample_rate=16000)

        live_session.close()
        assert live_session.closed is True

    asyncio.run(run())


def test_live_api_session_can_prepare_adk_live_session() -> None:
    async def run() -> None:
        session = LiveApiSession(runtime=ADKRuntime())

        live_session = await session.prepare_adk_live_session(user_id="tester", session_id="voice_session")

        assert live_session.ids.user_id == "tester"
        assert live_session.ids.session_id == "voice_session"
        live_session.close()

    asyncio.run(run())

