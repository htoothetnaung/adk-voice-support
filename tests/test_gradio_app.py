from app.ui.gradio_app import TRANSCRIPT_COLUMNS, clear_session, submit_turn


def test_submit_turn_adds_human_and_agent_transcript_rows() -> None:
    _, chat, rows, details, runner = submit_turn(
        "I want to talk to a human.",
        "Text",
        None,
        [],
        [],
    )

    assert runner is not None
    assert len(chat) == 2
    assert len(rows) == 2
    assert rows[0][0] == "Human"
    assert rows[1][0] == "Agent"
    assert rows[1][2] == "human_escalation_agent"
    assert details["intent"] == "human_escalation"


def test_clear_session_resets_ui_state() -> None:
    runner, chat, rows, details, transcript = clear_session()

    assert runner is not None
    assert chat == []
    assert rows == []
    assert details == {}
    assert transcript == ""


def test_transcript_columns_are_stable() -> None:
    assert TRANSCRIPT_COLUMNS == ["Speaker", "Transcript", "Agent", "Intent", "Tools", "Latency"]

