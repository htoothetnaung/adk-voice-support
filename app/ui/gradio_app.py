"""Optional Gradio UI for the simulator."""

from __future__ import annotations

from app.services import SupportAgentRunner


runner = SupportAgentRunner()


def respond(message: str, history: list[dict] | None = None) -> str:
    """Return a support response for Gradio."""

    del history
    return runner.run(message).final_response


def main() -> None:
    """Run a minimal Gradio chat UI."""

    try:
        import gradio as gr
    except ImportError as exc:  # pragma: no cover - optional UI dependency.
        raise RuntimeError("Install gradio to run this UI: python -m pip install gradio") from exc

    demo = gr.ChatInterface(fn=respond, title="Voice Support ADK Lab")
    demo.launch()


if __name__ == "__main__":
    main()

