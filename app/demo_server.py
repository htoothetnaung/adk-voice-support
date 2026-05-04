"""FastAPI browser demo with WebSocket event streaming."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from html import escape
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.services import SupportAgentRunner


app = FastAPI(title="Voice Support ADK Lab Demo")
_sessions: dict[str, SupportAgentRunner] = {}


class ChatRequest(BaseModel):
    """HTTP chat request."""

    message: str
    session_id: str = "http_demo"


class ChatResponse(BaseModel):
    """HTTP chat response."""

    session_id: str
    response: dict


def _session_key(user_id: str, session_id: str) -> str:
    return f"{user_id}:{session_id}"


def _get_runner(user_id: str, session_id: str) -> SupportAgentRunner:
    key = _session_key(user_id, session_id)
    if key not in _sessions:
        _sessions[key] = SupportAgentRunner()
    return _sessions[key]


def _tool_names(tool_calls: list[dict]) -> list[str]:
    return [tool_call["name"] for tool_call in tool_calls]


async def _word_chunks(text: str, chunk_size: int = 7) -> AsyncIterator[str]:
    words = text.split()
    for index in range(0, len(words), chunk_size):
        yield " ".join(words[index : index + chunk_size])
        await asyncio.sleep(0.01)


@app.get("/health")
def health() -> dict:
    """Health check used by tests and local smoke checks."""

    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Single-turn HTTP fallback for environments without WebSocket."""

    runner = _get_runner("http_user", request.session_id)
    response = runner.run(request.message)
    return ChatResponse(session_id=request.session_id, response=response.to_dict())


@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str) -> None:
    """WebSocket demo endpoint with human/agent/tool events."""

    await websocket.accept()
    runner = _get_runner(user_id, session_id)
    await websocket.send_json(
        {
            "type": "session_ready",
            "user_id": user_id,
            "session_id": session_id,
            "message": "Connected to Voice Support ADK Lab demo.",
        }
    )

    try:
        while True:
            payload = await websocket.receive_json()
            message_type = payload.get("type", "text")
            message = str(payload.get("text", "")).strip()
            if message_type == "close":
                await websocket.send_json({"type": "session_closed", "session_id": session_id})
                break
            if not message:
                await websocket.send_json({"type": "error", "message": "Message text is required."})
                continue

            await websocket.send_json({"type": "human_transcript", "text": message})
            response = runner.run(message)
            await websocket.send_json(
                {
                    "type": "intent_detected",
                    "intent": response.intent,
                    "agent": response.selected_agent,
                    "latency_ms": response.latency_ms,
                }
            )
            for tool_call in response.tool_calls:
                await websocket.send_json(
                    {
                        "type": "tool_call",
                        "name": tool_call["name"],
                        "result": tool_call["result"],
                    }
                )

            streamed = ""
            async for chunk in _word_chunks(response.final_response):
                streamed = f"{streamed} {chunk}".strip()
                await websocket.send_json({"type": "agent_delta", "text": chunk, "accumulated": streamed})

            await websocket.send_json(
                {
                    "type": "agent_transcript",
                    "text": response.final_response,
                    "agent": response.selected_agent,
                    "intent": response.intent,
                    "tools": _tool_names(response.tool_calls),
                    "latency_ms": response.latency_ms,
                }
            )
            await websocket.send_json({"type": "turn_complete", "response": response.to_dict()})
    except WebSocketDisconnect:
        return


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    """Serve the complete local browser demo."""

    session_id = f"demo_{uuid4().hex[:8]}"
    return HTMLResponse(DEMO_HTML.replace("__SESSION_ID__", escape(session_id)))


DEMO_HTML = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Voice Support ADK Lab</title>
  <style>
    :root {
      --bg: #f6f7f9;
      --panel: #ffffff;
      --border: #d8dee9;
      --text: #1f2937;
      --muted: #667085;
      --accent: #0f766e;
      --agent: #eef7f5;
      --human: #eff4ff;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--text); }
    header {
      height: 64px; border-bottom: 1px solid var(--border); background: var(--panel);
      display: flex; align-items: center; justify-content: space-between; padding: 0 24px;
    }
    h1 { font-size: 20px; margin: 0; }
    .status { color: var(--muted); font-size: 13px; }
    main { display: grid; grid-template-columns: minmax(420px, 1.3fr) minmax(360px, .9fr); gap: 16px; padding: 16px; }
    section { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; min-width: 0; }
    .section-head { padding: 12px 14px; border-bottom: 1px solid var(--border); font-weight: 650; }
    #chat { height: calc(100vh - 250px); min-height: 390px; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
    .bubble { max-width: 84%; padding: 11px 12px; border-radius: 8px; line-height: 1.45; white-space: pre-wrap; }
    .human { background: var(--human); align-self: flex-end; }
    .agent { background: var(--agent); align-self: flex-start; }
    .composer { border-top: 1px solid var(--border); padding: 12px; display: grid; grid-template-columns: 1fr auto; gap: 10px; }
    textarea, input, select {
      width: 100%; border: 1px solid var(--border); border-radius: 8px; padding: 10px; font: inherit; background: white; color: var(--text);
    }
    textarea { resize: vertical; min-height: 74px; }
    button {
      border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px; font: inherit; cursor: pointer; background: white;
    }
    button.primary { background: var(--accent); border-color: var(--accent); color: white; }
    button.active { background: #991b1b; border-color: #991b1b; color: white; }
    .side { display: flex; flex-direction: column; gap: 16px; }
    .controls { padding: 12px; display: grid; gap: 10px; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    #events { height: calc(100vh - 374px); min-height: 300px; overflow-y: auto; padding: 10px; display: grid; gap: 8px; align-content: start; }
    .event { border: 1px solid var(--border); border-radius: 8px; padding: 9px; background: #fff; }
    .event strong { display: block; font-size: 12px; color: var(--muted); margin-bottom: 4px; text-transform: uppercase; letter-spacing: .02em; }
    #liveTranscript { min-height: 106px; }
    .meta { color: var(--muted); font-size: 12px; }
    @media (max-width: 900px) { main { grid-template-columns: 1fr; } #chat, #events { height: 420px; } }
  </style>
</head>
<body>
  <header>
    <h1>Voice Support ADK Lab</h1>
    <div class="status" id="connectionStatus">Connecting...</div>
  </header>
  <main>
    <section>
      <div class="section-head">Conversation</div>
      <div id="chat"></div>
      <div class="composer">
        <textarea id="messageInput" placeholder="Type a customer request..."></textarea>
        <button class="primary" id="sendText">Send</button>
      </div>
    </section>
    <div class="side">
      <section>
        <div class="section-head">Mic & Transcript</div>
        <div class="controls">
          <div class="row">
            <button id="micButton">Mic off</button>
            <button class="primary" id="sendTranscript">Send transcript</button>
          </div>
          <textarea id="liveTranscript" placeholder="Live browser transcription appears here. You can edit before sending."></textarea>
          <div class="meta" id="micStatus">Browser mic is idle.</div>
        </div>
      </section>
      <section>
        <div class="section-head">Live Timeline</div>
        <div id="events"></div>
      </section>
    </div>
  </main>
  <script>
    const sessionId = "__SESSION_ID__";
    const userId = "browser_user";
    const chat = document.getElementById("chat");
    const events = document.getElementById("events");
    const connectionStatus = document.getElementById("connectionStatus");
    const messageInput = document.getElementById("messageInput");
    const liveTranscript = document.getElementById("liveTranscript");
    const micButton = document.getElementById("micButton");
    const micStatus = document.getElementById("micStatus");
    let recognition = null;
    let micOn = false;
    let finalTranscript = "";
    let agentDraft = null;

    const ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws/${userId}/${sessionId}`);

    function addBubble(role, text) {
      const bubble = document.createElement("div");
      bubble.className = `bubble ${role}`;
      bubble.textContent = text;
      chat.appendChild(bubble);
      chat.scrollTop = chat.scrollHeight;
      return bubble;
    }

    function addEvent(type, text, meta = "") {
      const item = document.createElement("div");
      item.className = "event";
      item.innerHTML = `<strong>${type}</strong><div>${escapeHtml(text)}</div>${meta ? `<div class="meta">${escapeHtml(meta)}</div>` : ""}`;
      events.prepend(item);
    }

    function escapeHtml(value) {
      return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char]));
    }

    function sendMessage(text) {
      const clean = text.trim();
      if (!clean || ws.readyState !== WebSocket.OPEN) return;
      ws.send(JSON.stringify({ type: "text", text: clean }));
      messageInput.value = "";
      liveTranscript.value = "";
      finalTranscript = "";
    }

    ws.onopen = () => { connectionStatus.textContent = "Connected"; };
    ws.onclose = () => { connectionStatus.textContent = "Disconnected"; };
    ws.onerror = () => { connectionStatus.textContent = "WebSocket error"; };
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "session_ready") addEvent("Session", data.message, data.session_id);
      if (data.type === "human_transcript") {
        addBubble("human", data.text);
        addEvent("Human", data.text);
        agentDraft = null;
      }
      if (data.type === "intent_detected") addEvent("Intent", data.intent, `${data.agent} · ${data.latency_ms}ms`);
      if (data.type === "tool_call") addEvent("Tool", data.name);
      if (data.type === "agent_delta") {
        if (!agentDraft) agentDraft = addBubble("agent", "");
        agentDraft.textContent = data.accumulated;
        chat.scrollTop = chat.scrollHeight;
      }
      if (data.type === "agent_transcript") {
        if (!agentDraft) agentDraft = addBubble("agent", data.text);
        agentDraft.textContent = data.text;
        addEvent("Agent", data.text, `${data.agent} · ${data.intent} · tools: ${data.tools.join(", ") || "none"}`);
      }
      if (data.type === "error") addEvent("Error", data.message);
    };

    document.getElementById("sendText").onclick = () => sendMessage(messageInput.value);
    document.getElementById("sendTranscript").onclick = () => sendMessage(liveTranscript.value);
    messageInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage(messageInput.value);
      }
    });

    micButton.onclick = () => {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        micStatus.textContent = "Browser speech recognition is not supported. Use Chrome or Edge.";
        return;
      }
      if (!recognition) {
        recognition = new SpeechRecognition();
        recognition.lang = "en-US";
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.onresult = (event) => {
          let interim = "";
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const text = event.results[i][0].transcript;
            if (event.results[i].isFinal) finalTranscript += text + " ";
            else interim += text;
          }
          liveTranscript.value = (finalTranscript + interim).trim();
        };
        recognition.onerror = (event) => { micStatus.textContent = `Mic error: ${event.error}`; };
        recognition.onend = () => {
          if (micOn) recognition.start();
        };
      }
      micOn = !micOn;
      if (micOn) {
        finalTranscript = "";
        liveTranscript.value = "";
        recognition.start();
        micButton.textContent = "Mic on";
        micButton.classList.add("active");
        micStatus.textContent = "Listening...";
      } else {
        recognition.stop();
        micButton.textContent = "Mic off";
        micButton.classList.remove("active");
        micStatus.textContent = "Mic stopped.";
      }
    };
  </script>
</body>
</html>
"""


def main() -> None:
    """Run the browser demo server."""

    import uvicorn

    uvicorn.run("app.demo_server:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
