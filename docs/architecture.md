# Architecture

The project has two runtime layers:

- ADK-compatible agent definitions in `app/agents/` for ADK Web discovery.
- A deterministic local `SupportAgentRunner` in `app/services/adk_runner.py` for CLI, tests, and evals without API calls.

High-level text flow:

```text
User message -> IntentDetector -> selected specialist -> mock tools -> SupportResponse -> trace/eval output
```

Specialists:

- `billing_agent`
- `technical_support_agent`
- `policy_agent`
- `human_escalation_agent`

The deterministic runner is the current execution path. The ADK agent objects preserve the intended Google ADK architecture for later model-backed operation.

## ADK Runtime Layer

`app.services.adk_runtime.ADKRuntime` adds official ADK lifecycle boundaries:

- reusable `Runner` and `InMemorySessionService`
- get-or-create session handling
- session-specific `RunConfig`
- one fresh `LiveRequestQueue` per live streaming session
- helpers for upstream text/audio and downstream event serialization

The local simulator still uses `SupportAgentRunner` by default so tests, CLI, and UI remain offline-safe.

## ADK Web

ADK Web compatibility lives in `adk_agents/voice_support/agent.py`.

Run it with:

```powershell
uv run adk web --session_service_uri=memory:// --port 8001 adk_agents
```

This app uses a custom ADK `BaseAgent` so ADK Web works without external model credentials. It emits function-call events, function-response events, and the final model response event, all backed by the same deterministic support runner.

## Browser Demo

`app.demo_server` is the full local demo surface. It serves a browser UI and a WebSocket endpoint:

- `GET /` browser support console
- `GET /health` health check
- `POST /api/chat` HTTP chat fallback
- `WS /ws/{user_id}/{session_id}` live human, intent, tool, agent delta, agent transcript, and turn-complete events

The endpoint is intentionally offline-safe and uses `SupportAgentRunner` today. The official ADK runtime layer is available for replacing the deterministic path with `runner.run_live()` when real provider credentials and browser audio forwarding are enabled.
