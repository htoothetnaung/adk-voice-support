# ADK Streaming Alignment

This backend follows the official ADK Gemini Live API Toolkit lifecycle while keeping the default simulator offline-safe.

## Official Lifecycle Mapping

- Application initialization: `app.services.adk_runtime.ADKRuntime` owns one reusable `InMemorySessionService` and `Runner`.
- Session initialization: `ADKRuntime.get_or_create_session()` checks for an existing session before creating one.
- Run configuration: `ADKRuntime.build_run_config()` creates session-specific `RunConfig` with `StreamingMode.BIDI`, audio response modality, transcription configs, and session resumption.
- Live request queue: `ADKRuntime.create_live_session()` creates a fresh `LiveRequestQueue` for each streaming session.
- Upstream messages: `ADKRuntime.send_text()` and `ADKRuntime.send_audio()` send content/audio into the per-session queue.
- Downstream events: `ADKRuntime.iter_live_events()` wraps `runner.run_live()` and `serialize_event()` prepares events for WebSocket/SSE delivery.
- Cleanup: `ADKLiveSession.close()` closes the queue once and records the closed state.

## Current Execution Paths

- `SupportAgentRunner` remains the deterministic local runner for CLI, Gradio, tests, and evals.
- `LiveApiSession.prepare_adk_live_session()` prepares official ADK streaming resources for the future real Live API transport.
- Transcript-driven voice simulations still avoid external network calls by default.

## Production Gap Still Remaining

The next production hardening step is a FastAPI WebSocket endpoint that runs concurrent upstream/downstream tasks, forwards browser audio/text into `LiveRequestQueue`, streams `run_live()` events back to the browser, and closes the queue in a `finally` block.

