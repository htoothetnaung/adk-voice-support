from app.services.interrupt_handler import InterruptHandler
from app.voice.audio_manager import AudioManager


def test_server_interrupt_clears_speaking_state() -> None:
    handler = InterruptHandler()
    handler.start_agent_speech()

    result = handler.handle_server_interrupt()

    assert result.interrupted is True
    assert result.source == "server"
    assert handler.is_speaking is False


def test_client_interrupt_ignored_when_not_speaking() -> None:
    result = InterruptHandler().handle_client_speech_detected()

    assert result.interrupted is False
    assert result.action == "continue_listening"


def test_audio_manager_clear_playback() -> None:
    manager = AudioManager()
    manager.output_buffer.append(b"abc")

    manager.clear_playback()

    assert manager.output_buffer.read_all() == b""

