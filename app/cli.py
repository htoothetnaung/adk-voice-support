"""Command-line entrypoint for the support simulator."""

from __future__ import annotations

from app.services import SupportAgentRunner
from app.services.trace_logger import TraceLogger
from app.voice import LiveApiSession, VoicePipelineRunner


def run_text_mode() -> None:
    """Run an interactive text chat loop."""

    runner = SupportAgentRunner()
    logger = TraceLogger()
    print("Voice Support ADK Lab - Text Mode")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        user_message = input("\nCustomer: ").strip()
        if user_message.lower() in {"exit", "quit"}:
            break
        if not user_message:
            continue

        response = runner.run(user_message)
        logger.save_turn(response)
        print(f"Agent ({response.selected_agent}): {response.final_response}")
        print(f"Intent: {response.intent} | Tools: {', '.join(call['name'] for call in response.tool_calls) or 'none'}")


def run_voice_mode(mode: str) -> None:
    """Run a transcript-driven voice simulation loop."""

    if mode == "live_api":
        session = LiveApiSession()
        label = "Gemini Live API simulation"
    else:
        session = VoicePipelineRunner()
        label = "TTS/STT pipeline simulation"

    print(f"Voice Support ADK Lab - {label}")
    print("Type a transcript as simulated microphone input. Type 'exit' or 'quit' to stop.")

    while True:
        transcript = input("\nTranscript: ").strip()
        if transcript.lower() in {"exit", "quit"}:
            break
        if not transcript:
            continue

        result = session.run_transcript_turn(transcript)
        print(f"Voice response ({result.approach}): {result.text_response}")
        print(f"Mock audio bytes: {len(result.audio_bytes)} | Latency: {result.latency_ms}ms")


def main() -> None:
    """Start the CLI."""

    print("Select mode:")
    print("[1] Text mode")
    print("[2] Voice - Gemini Live API simulation")
    print("[3] Voice - TTS/STT Pipeline simulation")
    choice = input("Choice [1]: ").strip() or "1"
    if choice == "2":
        run_voice_mode("live_api")
    elif choice == "3":
        run_voice_mode("pipeline")
    else:
        run_text_mode()


if __name__ == "__main__":
    main()
