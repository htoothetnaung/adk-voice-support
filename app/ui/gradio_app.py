"""Gradio support console with text and browser-mic transcript input."""

from __future__ import annotations

from typing import Any

from app.services import SupportAgentRunner


TRANSCRIPT_COLUMNS = ["Speaker", "Transcript", "Agent", "Intent", "Tools", "Latency"]


def _tool_names(response: Any) -> str:
    names = [call["name"] for call in response.tool_calls]
    return ", ".join(names) if names else "none"


def _new_runner() -> SupportAgentRunner:
    return SupportAgentRunner()


def submit_turn(
    message: str,
    mode: str,
    runner: SupportAgentRunner | None,
    chat_history: list[dict] | None,
    transcript_rows: list[list[str]] | None,
) -> tuple[str, list[dict], list[list[str]], dict, SupportAgentRunner]:
    """Process one text or mic transcript turn."""

    active_runner = runner or _new_runner()
    chat = list(chat_history or [])
    rows = list(transcript_rows or [])
    clean_message = (message or "").strip()
    if not clean_message:
        return "", chat, rows, {"status": "empty"}, active_runner

    response = active_runner.run(clean_message)
    tools = _tool_names(response)
    chat.extend(
        [
            {"role": "user", "content": clean_message},
            {"role": "assistant", "content": response.final_response},
        ]
    )
    rows.extend(
        [
            ["Human", clean_message, "-", "-", "-", "-"],
            [
                "Agent",
                response.final_response,
                response.selected_agent,
                response.intent,
                tools,
                f"{response.latency_ms} ms",
            ],
        ]
    )
    details = {
        "mode": mode,
        "selected_agent": response.selected_agent,
        "intent": response.intent,
        "latency_ms": response.latency_ms,
        "tools": [call["name"] for call in response.tool_calls],
    }
    return "", chat, rows, details, active_runner


def clear_session() -> tuple[SupportAgentRunner, list[dict], list[list[str]], dict, str]:
    """Reset the UI and runner state."""

    return _new_runner(), [], [], {}, ""


MIC_TOGGLE_JS = """
(enabled) => {
  const transcriptBox = document.querySelector('#live-transcript textarea');
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    return 'Mic unavailable: browser speech recognition is not supported.';
  }

  if (!window.voiceSupportRecognition) {
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = true;
    recognition.interimResults = true;
    window.voiceSupportFinalTranscript = '';

    recognition.onresult = (event) => {
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const text = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          window.voiceSupportFinalTranscript += text + ' ';
        } else {
          interim += text;
        }
      }
      if (transcriptBox) {
        transcriptBox.value = (window.voiceSupportFinalTranscript + interim).trim();
        transcriptBox.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText' }));
      }
    };

    recognition.onerror = (event) => {
      const status = document.querySelector('#mic-status textarea');
      if (status) {
        status.value = `Mic error: ${event.error}`;
        status.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText' }));
      }
    };

    window.voiceSupportRecognition = recognition;
  }

  if (enabled) {
    window.voiceSupportFinalTranscript = '';
    if (transcriptBox) {
      transcriptBox.value = '';
      transcriptBox.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'deleteContentBackward' }));
    }
    window.voiceSupportRecognition.start();
    return 'Mic on';
  }

  window.voiceSupportRecognition.stop();
  return 'Mic off';
}
"""


CSS = """
:root {
  --support-bg: #f7f8fb;
  --support-border: #d8dee9;
  --support-text: #1f2937;
  --support-muted: #667085;
  --support-accent: #0f766e;
}

.gradio-container {
  background: var(--support-bg);
  color: var(--support-text);
}

#top-band {
  border-bottom: 1px solid var(--support-border);
  padding: 12px 0 14px;
}

#top-band h1 {
  font-size: 22px;
  line-height: 1.2;
  margin: 0;
}

#top-band p {
  color: var(--support-muted);
  margin: 4px 0 0;
}

#chatbot {
  min-height: 520px;
}

#transcript-table {
  min-height: 420px;
}

#mic-status textarea {
  min-height: 42px !important;
}

#live-transcript textarea {
  min-height: 120px !important;
}

.primary-action {
  background: var(--support-accent) !important;
  border-color: var(--support-accent) !important;
}
"""


def create_demo():
    """Create the Gradio Blocks UI."""

    try:
        import gradio as gr
    except ImportError as exc:  # pragma: no cover - optional UI dependency.
        raise RuntimeError("Install Gradio with: uv sync --extra dev --extra ui") from exc

    with gr.Blocks(title="Voice Support ADK Lab") as demo:
        runner_state = gr.State(_new_runner())
        transcript_state = gr.State([])

        with gr.Row(elem_id="top-band"):
            gr.Markdown("# Voice Support ADK Lab\nMinimal support console")

        with gr.Row(equal_height=True):
            with gr.Column(scale=7, min_width=520):
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=560,
                    elem_id="chatbot",
                    buttons=["copy"],
                )
                with gr.Row():
                    message_box = gr.Textbox(
                        label="Text input",
                        placeholder="Type a customer request...",
                        lines=2,
                        max_lines=4,
                        scale=6,
                    )
                    send_button = gr.Button("Send", variant="primary", scale=1, elem_classes=["primary-action"])

            with gr.Column(scale=5, min_width=420):
                mode = gr.Radio(
                    choices=["Text", "Gemini Live simulation", "Pipeline simulation"],
                    value="Text",
                    label="Mode",
                )
                mic_toggle = gr.Checkbox(value=False, label="Mic")
                mic_status = gr.Textbox(value="Mic off", label="Mic status", interactive=False, elem_id="mic-status")
                live_transcript = gr.Textbox(
                    label="Live transcript",
                    placeholder="Mic transcript appears here. You can edit before sending.",
                    lines=5,
                    elem_id="live-transcript",
                )
                send_transcript_button = gr.Button("Send transcript", variant="primary", elem_classes=["primary-action"])
                clear_button = gr.Button("Clear session")

        with gr.Row():
            transcript_table = gr.Dataframe(
                headers=TRANSCRIPT_COLUMNS,
                datatype=["str", "str", "str", "str", "str", "str"],
                value=[],
                label="Transcript timeline",
                elem_id="transcript-table",
                interactive=False,
                type="array",
                wrap=True,
            )

        details = gr.JSON(label="Last turn")

        send_inputs = [message_box, mode, runner_state, chatbot, transcript_state]
        send_outputs = [message_box, chatbot, transcript_table, details, runner_state]
        transcript_outputs = [live_transcript, chatbot, transcript_table, details, runner_state]

        send_event = send_button.click(
            submit_turn,
            inputs=send_inputs,
            outputs=send_outputs,
            show_progress="minimal",
        )
        send_event.then(lambda rows: rows, inputs=transcript_table, outputs=transcript_state)

        submit_event = message_box.submit(
            submit_turn,
            inputs=send_inputs,
            outputs=send_outputs,
            show_progress="minimal",
        )
        submit_event.then(lambda rows: rows, inputs=transcript_table, outputs=transcript_state)

        transcript_event = send_transcript_button.click(
            submit_turn,
            inputs=[live_transcript, mode, runner_state, chatbot, transcript_state],
            outputs=transcript_outputs,
            show_progress="minimal",
        )
        transcript_event.then(lambda rows: rows, inputs=transcript_table, outputs=transcript_state)

        mic_toggle.change(
            fn=None,
            inputs=mic_toggle,
            outputs=mic_status,
            js=MIC_TOGGLE_JS,
            show_progress="hidden",
        )

        clear_event = clear_button.click(
            clear_session,
            outputs=[runner_state, chatbot, transcript_table, details, live_transcript],
            show_progress="hidden",
        )
        clear_event.then(lambda: [], outputs=transcript_state)

    return demo


def main() -> None:
    """Run the Gradio UI."""

    create_demo().launch(css=CSS)


if __name__ == "__main__":
    main()
