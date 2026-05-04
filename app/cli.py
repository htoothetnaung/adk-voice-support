"""Command-line entrypoint for the support simulator."""

from __future__ import annotations

from app.services import SupportAgentRunner
from app.services.trace_logger import TraceLogger


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


def main() -> None:
    """Start the CLI."""

    print("Select mode:")
    print("[1] Text mode")
    print("[2] Voice - Gemini Live API (coming in voice milestone)")
    print("[3] Voice - TTS/STT Pipeline (coming in voice milestone)")
    choice = input("Choice [1]: ").strip() or "1"
    if choice != "1":
        print("Voice modes are scaffolded in a later milestone. Starting text mode now.")
    run_text_mode()


if __name__ == "__main__":
    main()

