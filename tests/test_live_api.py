from app.voice.live_api_client import GeminiLiveApiClient
from app.voice.live_api_session import LiveApiSession


def test_live_api_client_offline_simulation() -> None:
    turn = GeminiLiveApiClient().simulate_turn("I want to talk to a human.")

    assert "escalation ticket" in turn.text_response
    assert turn.audio_bytes


def test_live_api_session_interrupt_clears_audio() -> None:
    result = LiveApiSession().run_transcript_turn("The app keeps crashing.", simulate_interrupt=True)

    assert result.interrupt is not None
    assert result.interrupt.interrupted is True
    assert result.audio_bytes == b""

