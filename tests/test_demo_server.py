from fastapi.testclient import TestClient

from app.demo_server import app


client = TestClient(app)


def test_demo_index_loads() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Voice Support ADK Lab" in response.text
    assert "WebSocket" in response.text


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_http_chat() -> None:
    response = client.post("/api/chat", json={"message": "I cannot log in.", "session_id": "test_http"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["response"]["selected_agent"] == "technical_support_agent"
    assert payload["response"]["intent"] == "technical_issue"


def test_websocket_streams_full_turn() -> None:
    with client.websocket_connect("/ws/tester/test_ws") as websocket:
        ready = websocket.receive_json()
        assert ready["type"] == "session_ready"

        websocket.send_json({"type": "text", "text": "I was charged twice. My email is alice@example.com."})
        event_types = []
        final_event = None
        for _ in range(20):
            event = websocket.receive_json()
            event_types.append(event["type"])
            if event["type"] == "turn_complete":
                final_event = event
                break

        assert "human_transcript" in event_types
        assert "intent_detected" in event_types
        assert "tool_call" in event_types
        assert "agent_delta" in event_types
        assert "agent_transcript" in event_types
        assert final_event is not None
        assert final_event["response"]["selected_agent"] == "billing_agent"

