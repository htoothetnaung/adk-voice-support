# Voice Architecture

The current voice layer is transcript-driven so it runs without microphones, API keys, or paid provider calls.

Approach A: Gemini Live API simulation

```text
Transcript -> LiveApiSession -> SupportAgentRunner -> mock audio bytes
```

Approach B: TTS/STT pipeline simulation

```text
Transcript -> MockSTTProvider -> SupportAgentRunner -> MockTTSProvider -> mock audio bytes
```

Shared pieces:

- `AudioManager`
- `InterruptHandler`
- `VoiceIntentDetector`
- `SimpleVAD`

Real provider integration remains explicit and guarded. Attempting real Deepgram/Gemini TTS behavior should require API keys and provider configuration, not silent fallback.

## ADK Live API Preparation

`LiveApiSession.prepare_adk_live_session()` prepares official ADK streaming resources through `ADKRuntime`.

This gives the next real provider pass a clean place to attach:

- FastAPI WebSocket accept/connect logic
- upstream browser text/audio to `LiveRequestQueue`
- downstream `runner.run_live()` events to the browser
- guaranteed queue cleanup in `finally`
