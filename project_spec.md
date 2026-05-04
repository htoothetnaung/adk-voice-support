# Project Spec: ADK Multi-Agent Voice Customer Support Simulator + Evaluation Lab

## 0. Project Summary

Build a Python backend using **Google Agent Development Kit (ADK)** for a bare-essential but realistic **multi-agent customer support simulator** with an integrated **evaluation lab**.

The first version does **not** need a beautiful UI. The priority is to prove that the system can:

1. Accept customer requests as text first.
2. Route the request to the correct specialist agent.
3. Use mock business tools.
4. Produce a useful support response.
5. Log agent routing, tool usage, latency, and final output.
6. Run automated evaluation scenarios.
7. **Add voice input/output with Gemini 3.1 Flash Live Preview (Audio-to-Audio) as the primary approach, with TTS/STT/LLM pipeline as a benchmarkable fallback.**
8. Later rebuild the same architecture using OpenAI Agents SDK for comparison.

This project should be treated as an engineering foundation, not a flashy demo.

---

## 1. Main Goal

Create a working **ADK-first multi-agent support backend** that can simulate how a company might build a real customer-support voice agent platform.

The system should have:

- A root triage/coordinator agent.
- Multiple specialist agents.
- Mock tools for customer, invoice, order, refund, ticket, and escalation workflows.
- A simple CLI or ADK Web interface for testing.
- A lightweight evaluation framework that checks routing accuracy, tool-call accuracy, response quality, and latency.
- **Dual voice architecture: Gemini Live API (A2A) as primary, TTS/STT/LLM pipeline as fallback/benchmark target.**
- **Intent detection and interrupt handling for both voice approaches.**
- A clean folder structure so the same project can later be rebuilt with OpenAI Agents SDK.

---

## 2. Why This Project Exists

The company asked us to review:

- Google ADK
- OpenAI Agents SDK

Instead of only reading documentation, we will build the same practical customer-support system in both frameworks.

This first version focuses on **Google ADK** because we already reviewed most of the ADK documentation.

Later, we will create a second implementation using OpenAI Agents SDK and compare:

- Agent declaration style
- Multi-agent routing
- Tool calling
- Handoff behavior
- Session handling
- Evaluation support
- Voice-readiness
- Developer experience

---

## 3. Project Name

Recommended name:

```text
voice-support-adk-lab
```

Alternative names:

```text
adk-voice-support-eval-lab
multi-agent-support-adk
voiceflow-adk-support-simulator
```

Use this name for now:

```text
voice-support-adk-lab
```

---

## 4. Core Scope for Version 1

### Version 1 Must Include

- Python backend.
- Google ADK agent definitions.
- Root triage agent.
- Billing specialist agent.
- Technical support specialist agent.
- Policy/FAQ specialist agent.
- Human escalation specialist agent.
- Mock tools.
- CLI runner.
- Basic ADK Web compatibility.
- Evaluation scenarios stored as JSON/YAML.
- Custom evaluation runner script.
- Logs saved per conversation.
- **Gemini 3.1 Flash Live Preview integration (WebSocket A2A).**
- **TTS/STT/LLM pipeline as fallback and benchmark baseline.**
- **Intent detection module for voice inputs.**
- **Interrupt detection and handling for both approaches.**
- **Voice evaluation benchmarks comparing A2A vs pipeline latency, quality, and accuracy.**

### Version 1 Does Not Need

- Beautiful frontend.
- Real telephony integration.
- Twilio integration.
- Production database.
- Real company data.
- Real payment/refund API.
- Perfect voice latency.
- Advanced memory.
- Authentication.
- Deployment.

---

## 5. Version Roadmap

### V0: Backend Text-Only Foundation

Goal: Get the multi-agent system working through text input.

Features:

- CLI chat loop.
- Triage agent routes to specialists.
- Specialist agents call tools.
- Logs conversation traces.
- Saves structured output.

### V1: Evaluation Lab

Goal: Automatically test the agent system.

Features:

- Evaluation dataset with predefined support scenarios.
- Expected intent.
- Expected specialist agent.
- Expected tools.
- Expected outcome.
- Evaluation runner.
- Metrics report.

### V2: Simple UI

Goal: Make the system easy to demo.

Options:

- ADK Web first.
- Streamlit second.
- Gradio third.

Do not overbuild the UI.

### V3: Voice Layer — Dual Architecture

Goal: Add voice input/output with **two comparable approaches**.

**Approach A: Gemini 3.1 Flash Live Preview (Primary)**
- Native audio-to-audio (A2A) via WebSocket.
- Sub-second latency.
- Built-in barge-in/interrupt detection.
- Built-in VAD (Voice Activity Detection).
- Native emotional tone adaptation.
- Tool calling within streaming context.
- Audio transcription provided.

**Approach B: TTS + STT + LLM Pipeline (Fallback / Benchmark)**
- STT: Deepgram / Whisper / faster-whisper.
- LLM: Standard ADK text agent.
- TTS: Gemini 3.1 Flash TTS Preview / pyttsx3 / ElevenLabs.
- Manual VAD and interrupt handling.
- Higher latency due to pipeline hops.

**V3 Evaluation:**
- Benchmark both approaches in the evaluation lab.
- Metrics: latency, interrupt accuracy, intent detection accuracy, voice quality, cost.

### V4: OpenAI Agents SDK Mirror

Goal: Rebuild the same project with OpenAI Agents SDK and compare both frameworks.

---

## 6. System Architecture

### High-Level Flow (Text)

```text
User message
    ↓
Root Triage Agent
    ↓
Intent classification / delegation
    ↓
Specialist Agent
    ↓
Mock business tool call
    ↓
Specialist response
    ↓
Final customer-facing response
    ↓
Trace log + evaluation record
```

### Voice Flow — Approach A: Gemini 3.1 Flash Live Preview (Primary)

```text
Microphone input (PCM 16kHz)
    ↓
WebSocket → Gemini Live API (gemini-3.1-flash-live-preview)
    ↓
[Native A2A processing: STT + LLM + TTS in single model]
    ↓
Audio response (PCM 24kHz) ← WebSocket
    ↓
Speaker output
    ↓
[Interrupt detected?] → Server sends 'interrupted' signal
    ↓
Clear playback buffer + restart turn
```

**Key differences from pipeline:**
- No separate STT/LLM/TTS stages.
- Single WebSocket connection.
- Server-side VAD and interrupt detection.
- Lower latency (sub-second first token).

### Voice Flow — Approach B: TTS + STT + LLM Pipeline (Fallback)

```text
Microphone input
    ↓
VAD (Voice Activity Detection) — local or server-side
    ↓
STT (Deepgram / Whisper / faster-whisper)
    ↓
Transcript
    ↓
ADK multi-agent backend (text)
    ↓
Text response
    ↓
TTS (Gemini 3.1 Flash TTS / pyttsx3 / ElevenLabs)
    ↓
Audio output
    ↓
[Interrupt detected?] → Local VAD cuts off TTS, sends new STT request
```

---

## 7. Agent Design

### 7.1 Root Agent: `support_triage_agent`

Purpose:

The root agent receives the user request and decides which specialist should handle the issue.

Responsibilities:

- Understand user intent.
- Route to the correct specialist agent.
- Avoid answering deeply specialized questions itself unless the answer is simple.
- Ask a clarification question if the request is ambiguous.
- Escalate to human support if the user is angry, asks for a human, or the task is sensitive.

Supported intents:

```text
billing_issue
technical_issue
policy_question
order_status
refund_request
account_issue
human_escalation
unknown
```

Expected behavior:

- If payment, invoice, charge, subscription, refund, or billing issue → Billing Agent.
- If login, app error, product not working, integration issue → Technical Support Agent.
- If terms, warranty, refund rules, privacy, cancellation policy → Policy Agent.
- If user asks for human, legal threat, complaint, angry tone, repeated failure → Escalation Agent.

---

### 7.2 Billing Agent: `billing_agent`

Purpose:

Handles billing, invoice, refund, charge, and subscription issues.

Tools:

- `lookup_customer`
- `lookup_invoice`
- `check_refund_eligibility`
- `create_refund_ticket`
- `create_support_ticket`

Example inputs:

```text
I was charged twice this month.
Can I get a refund?
My invoice amount is wrong.
I want to cancel my subscription.
```

Expected behavior:

- Ask for missing customer identifier if needed.
- Use mock lookup tools.
- Explain next steps clearly.
- Do not promise a refund unless tool result says eligible.
- Create a ticket when action is needed.

---

### 7.3 Technical Support Agent: `technical_support_agent`

Purpose:

Handles technical problems with the product or service.

Tools:

- `lookup_customer`
- `get_known_issues`
- `run_basic_diagnostic`
- `create_support_ticket`

Example inputs:

```text
I cannot log in.
The app keeps crashing.
My integration is not working.
I cannot receive OTP.
```

Expected behavior:

- Identify the issue category.
- Ask for relevant missing details.
- Run mock diagnostics.
- Suggest first-level troubleshooting.
- Escalate if the issue is unresolved.

---

### 7.4 Policy Agent: `policy_agent`

Purpose:

Answers company policy, FAQ, warranty, refund policy, privacy, and terms questions.

Tools:

- `search_policy_knowledge_base`
- `get_refund_policy`
- `get_cancellation_policy`
- `get_privacy_policy_summary`

Example inputs:

```text
What is your refund policy?
Can I cancel anytime?
How long is the warranty?
Do you store my data?
```

Expected behavior:

- Answer only from mock policy knowledge base.
- If policy is not found, say it cannot confirm.
- Avoid inventing rules.
- Escalate sensitive legal/privacy questions when necessary.

---

### 7.5 Human Escalation Agent: `human_escalation_agent`

Purpose:

Creates a clean handoff summary for a human support representative.

Tools:

- `create_escalation_ticket`
- `summarize_conversation_for_human`

Example inputs:

```text
I want to talk to a human.
This is unacceptable.
I already contacted support three times.
I want to file a complaint.
```

Expected behavior:

- Acknowledge the user calmly.
- Summarize the issue.
- Create an escalation ticket.
- Provide the ticket ID.

---

## 8. Tool Design

All tools should be mock Python functions first.

Do not connect real external APIs in V0/V1.

### 8.1 Mock Data

Create mock customer data:

```python
CUSTOMERS = {
    "cust_001": {
        "name": "Alice Chen",
        "email": "alice@example.com",
        "plan": "Pro",
        "status": "active"
    },
    "cust_002": {
        "name": "Min Thu",
        "email": "minthu@example.com",
        "plan": "Basic",
        "status": "active"
    }
}
```

Create mock invoice data:

```python
INVOICES = {
    "inv_1001": {
        "customer_id": "cust_001",
        "amount": 49.99,
        "status": "paid",
        "duplicate_charge": True
    },
    "inv_1002": {
        "customer_id": "cust_002",
        "amount": 19.99,
        "status": "paid",
        "duplicate_charge": False
    }
}
```

Create mock policy data:

```python
POLICIES = {
    "refund": "Customers may request a refund within 14 days if they meet eligibility requirements.",
    "cancellation": "Customers can cancel anytime. Access remains until the end of the billing period.",
    "privacy": "We store only necessary account and service usage data for support and billing."
}
```

---

### 8.2 Required Tools

Implement these tools:

```python
def lookup_customer(customer_id: str | None = None, email: str | None = None) -> dict:
    """Look up a mock customer by customer ID or email."""
```

```python
def lookup_invoice(invoice_id: str | None = None, customer_id: str | None = None) -> dict:
    """Look up mock invoice data."""
```

```python
def check_refund_eligibility(invoice_id: str) -> dict:
    """Check if a mock invoice is eligible for refund."""
```

```python
def create_refund_ticket(customer_id: str, invoice_id: str, reason: str) -> dict:
    """Create a mock refund support ticket."""
```

```python
def get_known_issues(product_area: str | None = None) -> dict:
    """Return mock known technical issues."""
```

```python
def run_basic_diagnostic(customer_id: str | None, issue_type: str) -> dict:
    """Run mock diagnostic for a technical issue."""
```

```python
def search_policy_knowledge_base(query: str) -> dict:
    """Search mock policy documents."""
```

```python
def create_support_ticket(customer_id: str | None, issue_type: str, summary: str) -> dict:
    """Create a generic mock support ticket."""
```

```python
def summarize_conversation_for_human(conversation: list[dict]) -> dict:
    """Create structured human handoff summary."""
```

```python
def create_escalation_ticket(summary: str, urgency: str = "medium") -> dict:
    """Create mock escalation ticket."""
```

---

## 9. Expected Folder Structure

Use this structure:

```text
voice-support-adk-lab/
│
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── cli.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── root_agent.py
│   │   ├── billing_agent.py
│   │   ├── technical_support_agent.py
│   │   ├── policy_agent.py
│   │   ├── escalation_agent.py
│   │   └── prompts.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── customer_tools.py
│   │   ├── billing_tools.py
│   │   ├── technical_tools.py
│   │   ├── policy_tools.py
│   │   └── escalation_tools.py
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── mock_customers.py
│   │   ├── mock_invoices.py
│   │   ├── mock_policies.py
│   │   └── mock_known_issues.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── adk_runner.py
│   │   ├── trace_logger.py
│   │   ├── response_parser.py
│   │   ├── intent_detector.py          # NEW: Intent detection for voice
│   │   └── interrupt_handler.py        # NEW: Interrupt handling abstraction
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── streamlit_app.py
│   │   └── gradio_app.py
│   │
│   └── voice/
│       ├── __init__.py
│       ├── live_api_client.py            # NEW: Gemini 3.1 Flash Live Preview client
│       ├── live_api_session.py           # NEW: WebSocket session manager
│       ├── stt.py                        # Fallback STT
│       ├── tts.py                        # Fallback TTS
│       ├── vad.py                        # Fallback VAD
│       ├── audio_manager.py              # NEW: Audio I/O buffer manager
│       ├── intent_detector_voice.py      # NEW: Voice-specific intent detection
│       └── pipeline_runner.py            # NEW: TTS/STT/LLM pipeline orchestrator
│
├── evals/
│   ├── eval_scenarios.json
│   ├── eval_scenarios_voice.json         # NEW: Voice-specific evaluation scenarios
│   ├── run_eval.py
│   ├── run_eval_voice.py                 # NEW: Voice evaluation runner
│   ├── metrics.py
│   ├── voice_metrics.py                  # NEW: Voice-specific metrics
│   └── reports/
│       └── .gitkeep
│
├── logs/
│   └── .gitkeep
│
├── tests/
│   ├── test_tools.py
│   ├── test_routing.py
│   ├── test_eval_metrics.py
│   ├── test_live_api.py                  # NEW: Live API client tests
│   ├── test_interrupt_handler.py         # NEW: Interrupt handling tests
│   └── test_intent_detector.py           # NEW: Intent detection tests
│
└── docs/
    ├── architecture.md
    ├── evaluation_design.md
    ├── voice_architecture.md             # NEW: Voice layer design doc
    └── openai_agents_sdk_mirror_plan.md
```

---

## 10. Environment Setup

Use Python 3.11+.

Recommended dependency manager:

```text
uv
```

But normal `venv` and `pip` are also fine.

### Basic Setup Commands

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows PowerShell

pip install --upgrade pip
pip install google-adk python-dotenv pydantic pytest rich streamlit gradio
```

### Voice Dependencies (Primary: Gemini Live API)

```bash
pip install google-genai websockets
```

### Voice Dependencies (Fallback: TTS/STT Pipeline)

```bash
pip install deepgram-sdk sounddevice scipy pyttsx3 faster-whisper
```

**Note:** Keep voice dependencies modular. The system should run in text-only mode if voice packages are not installed.

---

## 11. Environment Variables

Create `.env.example`:

```env
# Core
GOOGLE_API_KEY=your_google_api_key_here
ADK_MODEL=gemini-2.5-flash
APP_ENV=development
LOG_LEVEL=INFO

# Voice — Gemini Live API (Primary)
GEMINI_LIVE_MODEL=gemini-3.1-flash-live-preview
GEMINI_LIVE_API_ENDPOINT=wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent
ENABLE_LIVE_API=true

# Voice — TTS/STT Pipeline (Fallback)
STT_PROVIDER=deepgram  # Options: deepgram, whisper, faster-whisper
TTS_PROVIDER=gemini-tts  # Options: gemini-tts, pyttsx3, elevenlabs
DEEPGRAM_API_KEY=your_deepgram_key
ELEVENLABS_API_KEY=your_elevenlabs_key

# Audio Settings
AUDIO_INPUT_SAMPLE_RATE=16000
AUDIO_OUTPUT_SAMPLE_RATE=24000
AUDIO_CHUNK_SIZE_MS=20
VAD_AGGRESSIVENESS=2
```

`app/config.py` should load these values.

---

## 12. ADK Agent Implementation Requirements

### 12.1 Root Agent File

File:

```text
app/agents/root_agent.py
```

Responsibilities:

- Import all specialist agents.
- Create root triage agent.
- Attach specialist agents as sub-agents.
- Export `root_agent`.

Important:

ADK Web usually expects a discoverable `root_agent` object.

Example shape:

```python
from google.adk.agents import Agent
from app.config import settings
from app.agents.billing_agent import billing_agent
from app.agents.technical_support_agent import technical_support_agent
from app.agents.policy_agent import policy_agent
from app.agents.escalation_agent import human_escalation_agent

root_agent = Agent(
    name="support_triage_agent",
    model=settings.ADK_MODEL,
    description="Routes customer support requests to the correct specialist agent.",
    instruction=""
You are the root triage agent for a customer support system.
Your job is to understand the user's support request and delegate it to the most appropriate specialist agent.

Routing rules:
- Billing, invoice, payment, refund, duplicate charge, subscription payment -> billing_agent.
- Login issue, app crash, OTP issue, integration bug, product not working -> technical_support_agent.
- Refund rules, cancellation rules, privacy, warranty, terms, FAQ -> policy_agent.
- Angry customer, repeated failure, complaint, legal threat, direct request for human -> human_escalation_agent.

Do not invent tool results.
If information is missing, ask a short clarification question.
Keep the customer-facing tone professional, calm, and concise.
"",
    sub_agents=[
        billing_agent,
        technical_support_agent,
        policy_agent,
        human_escalation_agent,
    ],
)
```

Codex should verify exact ADK import names and adapt to the installed version if needed.

---

### 12.2 Billing Agent File

File:

```text
app/agents/billing_agent.py
```

Requirements:

- Define `billing_agent`.
- Attach billing tools.
- Instruct it to handle only billing/refund/subscription finance issues.

Behavior rules:

- Do not promise refunds without checking eligibility.
- Ask for invoice ID or customer email if missing.
- Create ticket when action is required.
- Return clear next steps.

---

### 12.3 Technical Support Agent File

File:

```text
app/agents/technical_support_agent.py
```

Requirements:

- Define `technical_support_agent`.
- Attach technical tools.
- Diagnose simple issues.
- Create support ticket if unresolved.

Behavior rules:

- Ask for customer ID/email if diagnostic requires customer context.
- Give first-level troubleshooting.
- Escalate if issue seems severe.

---

### 12.4 Policy Agent File

File:

```text
app/agents/policy_agent.py
```

Requirements:

- Define `policy_agent`.
- Attach policy tools.
- Answer only from mock policy source.

Behavior rules:

- Do not hallucinate company policy.
- If policy not found, say it cannot confirm.
- For legal/privacy-sensitive requests, suggest escalation.

---

### 12.5 Escalation Agent File

File:

```text
app/agents/escalation_agent.py
```

Requirements:

- Define `human_escalation_agent`.
- Attach escalation tools.
- Create human-readable handoff summary.

Behavior rules:

- Acknowledge frustration.
- Summarize issue.
- Create escalation ticket.
- Provide mock ticket ID.

---

## 13. Prompting Style

Keep prompts practical and constrained.

Every agent prompt should include:

```text
Role
Scope
Available tools
When to ask clarification
When to escalate
Output style
Forbidden behavior
```

Example output style:

```text
- Be concise.
- Use professional customer support tone.
- Do not mention internal agent names unless useful for debugging.
- Do not expose hidden routing logic.
- Do not fabricate customer, invoice, or policy details.
```

---

## 14. Logging and Tracing Requirements

Create:

```text
app/services/trace_logger.py
```

Each user interaction should produce a structured log:

```json
{
  "conversation_id": "conv_20260504_001",
  "timestamp": "2026-05-04T12:00:00+08:00",
  "user_message": "I was charged twice this month.",
  "detected_intent": "billing_issue",
  "expected_agent": null,
  "actual_agent": "billing_agent",
  "tool_calls": [
    {
      "tool_name": "lookup_invoice",
      "arguments": {"customer_id": "cust_001"},
      "success": true,
      "latency_ms": 20
    }
  ],
  "final_response": "I found a duplicate charge...",
  "total_latency_ms": 1240,
  "error": null,
  "voice_approach": "live_api",           // NEW: live_api | pipeline
  "voice_latency_ms": 800,                  // NEW: end-to-end voice latency
  "interrupt_count": 0,                     // NEW: number of interrupts
  "audio_transcript": "I was charged..."   // NEW: transcript from audio
}
```

At first, if exact ADK event-level tracing is difficult, implement a lightweight wrapper logger around app calls and tool functions.

The goal is not perfect tracing in V0. The goal is visible engineering instrumentation.

---

## 15. CLI Runner

Create:

```text
app/cli.py
```

CLI behavior:

```bash
python -m app.cli
```

Expected terminal flow:

```text
Voice Support ADK Lab
Type 'exit' to quit.

[1] Text mode
[2] Voice mode — Gemini Live API (Primary)
[3] Voice mode — TTS/STT Pipeline (Fallback)

Select mode: 2

Connecting to Gemini 3.1 Flash Live Preview...
Connected. Speak now (say 'quit' to exit).

🎤 [Listening...]
🤖 Agent: I can help check that. Could you provide your invoice ID or account email?

🎤 [Listening...]
🤖 Agent: I found your account and noticed a duplicate charge on invoice inv_1001. I created refund ticket ref_abc123 for review.
```

CLI should:

- Maintain a session ID.
- Send user message to ADK runner.
- Print final response.
- Save trace log.
- **For voice modes: handle audio I/O, interrupt signals, and mode selection.**

---

## 16. ADK Runner Service

Create:

```text
app/services/adk_runner.py
```

Responsibilities:

- Encapsulate ADK runtime calls.
- Accept user input.
- Return final response.
- Later expose same function to Streamlit/Gradio.

Suggested interface:

```python
class SupportAgentRunner:
    def __init__(self):
        ...

    async def run_message(
        self,
        user_id: str,
        session_id: str,
        message: str,
    ) -> dict:
        """Run one user message through the ADK multi-agent system."""
```

Return shape:

```python
{
    "response_text": "...",
    "events": [...],
    "latency_ms": 1234,
    "tool_calls": [...],
    "raw": {...}
}
```

If event parsing is difficult, return raw ADK events first and improve later.

---

## 17. Voice Layer — Gemini 3.1 Flash Live Preview (Primary)

### 17.1 Architecture

The Gemini Live API uses a **WebSocket-based bidirectional streaming protocol** (WSS) [^3^]. It is fundamentally different from the REST-based TTS/STT/LLM pipeline.

**Model:** `gemini-3.1-flash-live-preview` [^13^]

**Key capabilities:**
- **Audio-to-Audio (A2A):** Native audio input and output. No separate STT or TTS needed.
- **Sub-second latency:** First token in ~600ms [^9^].
- **Barge-in / Interrupt:** Server-side Voice Activity Detection (VAD) detects user speech during model output and sends an `interrupted` signal [^7^][^8^].
- **Tool use:** Function calling supported within streaming context (synchronous only in 3.1) [^13^].
- **Audio transcription:** Text transcripts of both user input and model output are provided.
- **Thinking levels:** Configurable via `thinkingLevel` (minimal, low, medium, high). Default is `minimal` for lowest latency [^13^].

**Technical specs:**
- Input: Audio (raw 16-bit PCM, 16kHz, little-endian), images (JPEG <= 1FPS), text [^3^]
- Output: Audio (raw 16-bit PCM, 24kHz, little-endian), text [^3^]
- Protocol: Stateful WebSocket connection [^3^]

### 17.2 Implementation Files

**`app/voice/live_api_client.py`**
- Wraps the GenAI SDK or raw WebSocket connection to Gemini Live API.
- Handles authentication (API key via OAuth).
- Sends `BidiGenerateContentSetup` configuration.
- Streams audio chunks to the API.
- Receives audio chunks + transcripts + tool calls + interrupt signals.

**`app/voice/live_api_session.py`**
- Manages the lifecycle of a Live API WebSocket session.
- Handles reconnection logic.
- Maintains session state across interrupts.

**`app/voice/audio_manager.py`**
- Manages microphone input (PCM 16kHz capture).
- Manages speaker output (PCM 24kHz playback).
- Handles audio buffer queue.
- On `interrupted` signal: clears playback buffer immediately [^8^].

**`app/voice/intent_detector_voice.py`**
- Extracts intent from Live API transcripts.
- Falls back to local intent classification if transcript is ambiguous.
- Maps voice-specific utterances to system intents (e.g., "I wanna talk to someone" → `human_escalation`).

### 17.3 Live API Configuration

```python
from google.genai import types

live_config = types.LiveConnectConfig(
    response_modalities=["AUDIO"],  # or ["AUDIO", "TEXT"] for transcripts
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
        )
    ),
    system_instruction="""You are a helpful customer support voice agent...""",
    tools=[...],  # Attach mock business tools
)
```

**Important migration notes from Gemini 2.5 Flash Live [^13^]:**
- Model string: `gemini-3.1-flash-live-preview`
- Thinking config: Use `thinkingLevel` instead of `thinkingBudget`. Default `minimal`.
- Server events: Single event can contain multiple content parts (audio + transcript). Handle all parts.
- Client content: Use `send_realtime_input` for ongoing text. `send_client_content` only for initial history.
- Async function calls: Not supported in 3.1. Tool calls are synchronous.
- Proactive audio and affective dialog: Not supported in 3.1. Remove these configs.

### 17.4 Interrupt Handling

The Live API handles **server-side interruption detection** via VAD [^7^][^8^]:

```python
async for response in session.receive():
    server_content = response.server_content

    if hasattr(server_content, "interrupted") and server_content.interrupted:
        print("🤐 INTERRUPTION DETECTED")
        audio_manager.interrupt()  # Clear local playback buffer
        # Model generation is already cancelled server-side

    if server_content and server_content.model_turn:
        for part in server_content.model_turn.parts:
            if part.inline_data:
                audio_manager.add_audio(part.inline_data.data)

    if server_content and server_content.turn_complete:
        print("✅ Turn complete")
```

**Client responsibilities:**
1. Listen for `interrupted` signal from server.
2. Immediately stop audio playback.
3. Clear audio playback queue to prevent "ghost" audio [^8^].
4. Resume listening for new user input.

---

## 18. Voice Layer — TTS/STT/LLM Pipeline (Fallback)

### 18.1 Architecture

Traditional 3-hop pipeline for comparison and fallback:

```text
Audio Input → VAD → STT → Text → ADK Agent → Text → TTS → Audio Output
```

**Latency characteristics:**
- VAD detection: ~100-300ms
- STT transcription: ~200-800ms
- LLM inference: ~500-2000ms
- TTS generation: ~200-1000ms
- **Total pipeline latency: ~1000-4100ms** (vs ~600-800ms for Live API)

### 18.2 Implementation Files

**`app/voice/stt.py`**
- STT providers: Deepgram, Whisper (OpenAI), faster-whisper (local).
- Returns transcript + confidence score.
- Handles streaming vs batch transcription.

**`app/voice/tts.py`**
- TTS providers: Gemini 3.1 Flash TTS Preview, pyttsx3 (local), ElevenLabs.
- Gemini TTS model: `gemini-3.1-flash-tts-preview` [^2^]
- Supports voice selection and director notes for style control [^2^].

**`app/voice/vad.py`**
- Voice Activity Detection.
- Options: WebRTC VAD (local), Deepgram streaming VAD, or server-side.
- Aggressiveness setting (0-3) [^5^].

**`app/voice/pipeline_runner.py`**
- Orchestrates the full pipeline.
- Manages audio buffers between stages.
- Handles pipeline interrupts (local VAD cuts off TTS, restarts STT).

### 18.3 Interrupt Handling (Pipeline)

Unlike Live API's server-side interrupt detection, the pipeline approach requires **client-side interrupt management**:

```python
class PipelineInterruptHandler:
    def __init__(self, vad, tts, stt):
        self.vad = vad
        self.tts = tts
        self.stt = stt
        self.is_speaking = False

    async def on_user_speech_detected(self):
        if self.is_speaking:
            # User is interrupting agent speech
            self.tts.stop()  # Stop current TTS playback
            self.stt.start_stream()  # Start new transcription
            self.is_speaking = False
```

---

## 19. Intent Detection

### 19.1 Purpose

Intent detection classifies user utterances (from voice or text) into system intents for routing.

### 19.2 Implementation

**`app/services/intent_detector.py`**

```python
class IntentDetector:
    SUPPORTED_INTENTS = [
        "billing_issue",
        "technical_issue",
        "policy_question",
        "order_status",
        "refund_request",
        "account_issue",
        "human_escalation",
        "unknown",
    ]

    def detect(self, text: str, context: list[dict] = None) -> dict:
        """
        Returns:
            {
                "intent": "billing_issue",
                "confidence": 0.92,
                "method": "keyword" | "llm" | "voice_transcript",
                "raw_text": "..."
            }
        """
```

**Detection methods (in order of speed):**
1. **Keyword/regex matching** (fast, deterministic): Map keywords to intents.
2. **LLM-based classification** (slower, more accurate): Use a lightweight model for ambiguous cases.
3. **Voice transcript metadata** (Live API only): Use confidence scores from audio transcription.

### 19.3 Voice-Specific Intent Detection

**`app/voice/intent_detector_voice.py`**

Voice inputs often have different patterns than text:
- "Hey uh, I think I was charged twice?" → `billing_issue`
- "I need a person" → `human_escalation`
- "What's your policy on refunds?" → `policy_question`

Handle:
- Disfluencies ("um", "uh", "like")
- Incomplete sentences
- Emotional tone indicators (shouting = escalation)

---

## 20. Evaluation Lab Design

### 20.1 Text Evaluation

Create:

```text
evals/eval_scenarios.json
```

Each scenario should include:

```json
{
  "id": "billing_duplicate_charge_001",
  "user_message": "I was charged twice this month. Can you help? My email is alice@example.com.",
  "expected_intent": "billing_issue",
  "expected_agent": "billing_agent",
  "expected_tools": ["lookup_customer", "lookup_invoice", "check_refund_eligibility", "create_refund_ticket"],
  "must_include": ["duplicate", "refund", "ticket"],
  "must_not_include": ["guaranteed", "definitely refunded"],
  "max_latency_ms": 8000
}
```

---

### 20.2 Voice Evaluation Scenarios

Create:

```text
evals/eval_scenarios_voice.json
```

Voice scenarios test both approaches (Live API and Pipeline) with the same inputs:

```json
{
  "id": "voice_billing_duplicate_001",
  "audio_input_file": "evals/audio_samples/billing_duplicate_001.wav",
  "transcript": "I was charged twice this month. My email is alice@example.com.",
  "expected_intent": "billing_issue",
  "expected_agent": "billing_agent",
  "expected_tools": ["lookup_customer", "lookup_invoice", "check_refund_eligibility"],
  "approach_a_live_api": {
    "max_latency_ms": 1500,
    "max_interrupt_latency_ms": 300,
    "expected_audio_output_duration_sec": 5.0
  },
  "approach_b_pipeline": {
    "max_latency_ms": 4000,
    "max_interrupt_latency_ms": 800,
    "expected_audio_output_duration_sec": 5.0
  },
  "must_include": ["duplicate", "refund"],
  "must_not_include": ["guaranteed"]
}
```

---

### 20.3 Voice Benchmark Metrics

**`evals/voice_metrics.py`**

Metrics for comparing the two voice approaches:

| Metric | Description | Target (Live API) | Target (Pipeline) |
|---|---|---|---|
| **End-to-end latency** | Audio in → Audio out first chunk | <= 1500ms | <= 4000ms |
| **First token latency** | Time to first audio byte | <= 600ms | <= 1500ms |
| **Interrupt detection latency** | User speaks → Interrupt signal | <= 300ms (server-side) | <= 800ms (client-side) |
| **Interrupt accuracy** | True positives / (True positives + False positives) | >= 95% | >= 85% |
| **Intent detection accuracy** | Correct intent / Total scenarios | >= 90% | >= 90% |
| **Transcription WER** | Word Error Rate for STT | N/A (native) | <= 10% |
| **Voice quality MOS** | Mean Opinion Score (1-5) | >= 4.0 | >= 3.5 |
| **Tool call success rate** | Successful tool calls / Attempts | >= 95% | >= 95% |
| **Cost per minute** | API cost for 1 min of conversation | TBD | TBD |

### 20.4 Voice Evaluation Runner

**`evals/run_eval_voice.py`**

```bash
python -m evals.run_eval_voice --approach live_api
python -m evals.run_eval_voice --approach pipeline
python -m evals.run_eval_voice --approach both --compare
```

Expected output:

```text
Running voice evaluation scenarios...

=== Approach A: Gemini 3.1 Flash Live Preview ===
[PASS] voice_billing_duplicate_001 — Latency: 820ms, Interrupt: 120ms
[PASS] voice_tech_login_001 — Latency: 750ms, Intent: billing_issue ✓
[FAIL] voice_escalation_001 — Interrupt latency: 450ms (target: 300ms)

Summary (Live API):
Total: 20 | Passed: 18 | Failed: 2
Avg latency: 890ms
Avg interrupt latency: 180ms
Intent accuracy: 95%

=== Approach B: TTS/STT/LLM Pipeline ===
[PASS] voice_billing_duplicate_001 — Latency: 3200ms, Interrupt: 600ms
[FAIL] voice_tech_login_001 — Latency: 4500ms (target: 4000ms)

Summary (Pipeline):
Total: 20 | Passed: 15 | Failed: 5
Avg latency: 3400ms
Avg interrupt latency: 720ms
Intent accuracy: 88%

=== Comparison ===
| Metric | Live API | Pipeline | Winner |
|---|---|---|---|
| Avg Latency | 890ms | 3400ms | Live API |
| Intent Accuracy | 95% | 88% | Live API |
| Interrupt Latency | 180ms | 720ms | Live API |
| Cost/min | $0.05 | $0.12 | Live API |

Report saved to: evals/reports/voice_eval_report_20260504_120000.json
```

---

## 21. Minimum Evaluation Scenarios

Start with at least 20 text scenarios + 10 voice scenarios.

### Text Scenarios (20+)

See original spec sections 18-20 for billing, technical, policy, and escalation scenarios.

### Voice Scenarios (10+)

Include:
- 3 billing scenarios (with disfluencies: "Um, I think I was charged...")
- 3 technical scenarios (with incomplete sentences: "App keeps crashing when I...")
- 2 policy scenarios (with follow-up questions)
- 2 escalation scenarios (with angry tone indicators)

---

## 22. Testing Requirements

Use `pytest`.

### Tool Tests

File:

```text
tests/test_tools.py
```

Test:
- Customer lookup by email.
- Invoice lookup by invoice ID.
- Refund eligibility returns correct result.
- Ticket creation returns ticket ID.
- Policy search returns expected policy text.

### Metric Tests

File:

```text
tests/test_eval_metrics.py
```

Test:
- Routing accuracy calculation.
- Tool recall calculation.
- Required phrase coverage.
- Forbidden phrase detection.
- Overall pass/fail logic.

### Routing Tests

File:

```text
tests/test_routing.py
```

Test with deterministic or mocked agent outputs if direct LLM calls are too unstable.

### Live API Tests

File:

```text
tests/test_live_api.py
```

Test:
- WebSocket connection establishment.
- Audio chunk streaming.
- Interrupt signal handling.
- Tool call within Live API session.
- Transcript extraction.

### Interrupt Handler Tests

File:

```text
tests/test_interrupt_handler.py
```

Test:
- Server-side interrupt detection (Live API mock).
- Client-side interrupt detection (pipeline VAD mock).
- Audio buffer clearing.
- Session state after interrupt.

### Intent Detector Tests

File:

```text
tests/test_intent_detector.py
```

Test:
- Keyword matching accuracy.
- LLM-based classification.
- Voice disfluency handling.
- Confidence scoring.

---

## 23. Simple UI Options

### Option A: ADK Web

Preferred first because this is an ADK project.

Requirement:

- Ensure `root_agent` is discoverable.
- Run ADK Web according to installed ADK version.

### Option B: Streamlit

Create:

```text
app/ui/streamlit_app.py
```

Features:

- Text input.
- Chat history.
- Show final answer.
- **Voice mode toggle (Live API vs Pipeline).**
- **Audio waveform visualization.**
- Expandable debug panel:
  - selected agent
  - tool calls
  - latency (overall + per-stage for pipeline)
  - raw events
  - interrupt count
  - intent detection confidence

### Option C: Gradio

Create:

```text
app/ui/gradio_app.py
```

Features:

- Chatbot interface.
- **Microphone input with mode selection.**
- **Audio output playback.**
- Debug text box.

For V0, CLI is enough. UI can come after backend works.

---

## 24. Voice Layer Implementation Phases

### Phase 3.1: Gemini Live API Client

Codex should:

1. Implement `app/voice/live_api_client.py` using `google-genai` SDK.
2. Implement `app/voice/live_api_session.py` for WebSocket lifecycle.
3. Implement `app/voice/audio_manager.py` for PCM audio I/O.
4. Add basic interrupt handling (listen for `interrupted` signal, clear buffer).
5. Add unit tests in `tests/test_live_api.py`.

Acceptance criteria:

```bash
python -m tests.test_live_api
```

passes (with mocked WebSocket).

### Phase 3.2: Intent Detection

Codex should:

1. Implement `app/services/intent_detector.py` for text intent detection.
2. Implement `app/voice/intent_detector_voice.py` for voice-specific intent detection.
3. Handle disfluencies and incomplete sentences.
4. Add unit tests in `tests/test_intent_detector.py`.

Acceptance criteria:

```bash
pytest tests/test_intent_detector.py
```

passes.

### Phase 3.3: TTS/STT Pipeline

Codex should:

1. Implement `app/voice/stt.py` with Deepgram and Whisper options.
2. Implement `app/voice/tts.py` with Gemini TTS and pyttsx3 options.
3. Implement `app/voice/vad.py` with WebRTC VAD.
4. Implement `app/voice/pipeline_runner.py` to orchestrate the pipeline.
5. Add client-side interrupt handling.
6. Add unit tests.

Acceptance criteria:

```bash
pytest tests/test_interrupt_handler.py
```

passes.

### Phase 3.4: Voice Evaluation

Codex should:

1. Create `evals/eval_scenarios_voice.json` with 10+ scenarios.
2. Implement `evals/voice_metrics.py`.
3. Implement `evals/run_eval_voice.py`.
4. Generate comparison reports.

Acceptance criteria:

```bash
python -m evals.run_eval_voice --approach both --compare
```

produces a JSON report with both approaches benchmarked.

---

## 25. README Requirements

The README should include:

```text
# Voice Support ADK Lab

## What this project is
## Architecture
## Agents
## Tools
## Evaluation Lab
## Voice Layer (Dual Architecture)
  - Gemini 3.1 Flash Live Preview (Primary)
  - TTS/STT/LLM Pipeline (Fallback)
## Setup
## Run CLI
## Run ADK Web
## Run Evaluation
## Run Voice Evaluation
## Run Streamlit/Gradio
## Project Roadmap
## Future OpenAI Agents SDK Version
```

Also include updated architecture diagrams for both voice approaches.

---

## 26. OpenAI Agents SDK Mirror Plan

Create:

```text
docs/openai_agents_sdk_mirror_plan.md
```

Write this note:

```text
This project is intentionally designed so the same system can later be rebuilt with OpenAI Agents SDK.

Keep these concepts framework-neutral:

- Agent names
- Tool names
- Evaluation scenarios
- Mock data
- Metrics
- CLI behavior
- UI behavior
- Voice approach abstraction (Live API vs Pipeline)

Only the agent runtime implementation should change.
```

Future comparison table:

```text
| Feature | Google ADK | OpenAI Agents SDK | Notes |
|---|---|---|---|
| Agent creation | TBD | TBD | |
| Sub-agent/handoff | TBD | TBD | |
| Tool calling | TBD | TBD | |
| Evaluation | TBD | TBD | |
| Voice support | TBD | TBD | |
| Live API integration | TBD | TBD | |
| Debugging | TBD | TBD | |
| Deployment | TBD | TBD | |
```

---

## 27. Engineering Rules for Codex

Codex must follow these rules:

1. Keep code simple and readable.
2. Do not over-engineer.
3. Prefer mock tools before real integrations.
4. Keep business logic deterministic where possible.
5. Add docstrings to every tool.
6. Keep prompts in separate files if they become long.
7. Do not put API keys in code.
8. Make CLI work before UI.
9. Make evaluation work before voice.
10. Keep OpenAI SDK mirror in mind but do not implement it yet.
11. **Gemini Live API is the primary voice approach. TTS/STT pipeline is fallback and benchmark target.**
12. **Intent detection and interrupt handling must work for both approaches.**
13. **All voice code should be modular — the system must run in text-only mode if voice deps are missing.**

---

## 28. Definition of Done for First Working Version

The first working version is done when:

```bash
python -m app.cli
```

can handle:

```text
I was charged twice this month. My email is alice@example.com.
I cannot log in to my account.
What is your cancellation policy?
I want to speak to a human.
```

and:

```bash
python -m evals.run_eval
```

produces:

```text
Routing accuracy
Tool recall
Required phrase coverage
Forbidden phrase violations
Latency summary
Overall pass/fail count
```

and:

```bash
python -m evals.run_eval_voice --approach live_api
```

produces:

```text
Voice latency metrics
Interrupt detection accuracy
Intent detection accuracy
Audio quality metrics
```

---

## 29. Stretch Goals

Only after the core system works:

### Stretch Goal 1: Filler Speech Controller

Add latency-aware filler messages.

### Stretch Goal 2: Advanced Interrupt Handling

- Handle overlapping speech in pipeline mode.
- Add interrupt recovery ("Sorry, you were saying?") in Live API mode.

### Stretch Goal 3: Real STT/TTS Providers

Integrate Deepgram, ElevenLabs, or Google TTS.

### Stretch Goal 4: Human Approval Flow

Before refund ticket creation, ask user confirmation.

### Stretch Goal 5: Persistent Sessions

Store sessions in SQLite.

### Stretch Goal 6: Framework Comparison Report

After OpenAI Agents SDK version exists, compare both.

### Stretch Goal 7: Multi-language Voice Support

Test Live API multilingual capabilities (70+ languages) [^3^].

---

## 30. Suggested First Codex Prompt

Use this prompt for Codex:

```text
You are helping me build a Python project called voice-support-adk-lab.

Goal:
Build a bare-essential Google ADK multi-agent customer support simulator with an evaluation lab.

Please implement Phase 1 and Phase 2 first:
1. Create the project folder structure.
2. Add Python package files.
3. Add config loader using python-dotenv.
4. Add mock data files for customers, invoices, policies, and known technical issues.
5. Add mock tool functions for customer lookup, invoice lookup, refund eligibility, support ticket creation, known issue lookup, diagnostics, policy search, conversation summary, and escalation ticket creation.
6. Add unit tests for all tools.
7. Add README skeleton.

Important:
- Use Google ADK later, but for this first step focus on project structure and tools.
- Keep everything deterministic and simple.
- Do not connect real external APIs.
- Do not build UI yet.
- Do not implement voice yet.
- Make sure pytest passes.

After implementation, show me the file tree and commands to run tests.
```

---

## 31. Suggested Second Codex Prompt

After Phase 1 and 2 pass, use:

```text
Now implement Phase 3 and Phase 4.

Goal:
Add Google ADK agents and a CLI runner.

Requirements:
1. Create billing_agent, technical_support_agent, policy_agent, and human_escalation_agent.
2. Create support_triage_agent as root_agent.
3. Attach the specialist agents as sub_agents.
4. Attach the correct mock tools to each specialist agent.
5. Implement app/services/adk_runner.py to run messages through the ADK root agent.
6. Implement app/cli.py as an interactive terminal chat.
7. Add structured trace logging to logs/.
8. Make sure importing root_agent works.
9. Make sure python -m app.cli runs.

Important:
- Use the installed google-adk package API.
- If an import or runner API differs from expected docs, inspect the installed package and adapt.
- Keep prompts practical and short.
- Do not build UI yet.
- Do not implement voice yet.
```

---

## 32. Suggested Third Codex Prompt

After CLI works, use:

```text
Now implement Phase 5: Evaluation Lab.

Requirements:
1. Create evals/eval_scenarios.json with at least 20 scenarios.
2. Implement evals/metrics.py.
3. Implement evals/run_eval.py.
4. Evaluation should call the same SupportAgentRunner used by CLI.
5. For each scenario, record:
   - expected_agent
   - actual_agent
   - expected_tools
   - actual_tools
   - routing_correct
   - tool_recall
   - required_phrase_coverage
   - forbidden_phrase_violation
   - latency_ms
   - pass/fail
6. Save JSON report to evals/reports/.
7. Print summary in terminal.

Important:
- If exact actual_agent/tool_calls cannot be extracted from ADK events yet, implement best-effort extraction and store raw events for debugging.
- Keep the evaluation code independent from UI.
```

---

## 33. Suggested Fourth Codex Prompt (Voice Layer)

After text evaluation works, use:

```text
Now implement Phase 6: Voice Layer — Dual Architecture.

Goal:
Add voice support with TWO approaches: Gemini Live API (primary) and TTS/STT Pipeline (fallback).

Requirements:

### Approach A: Gemini 3.1 Flash Live Preview (Primary)
1. Implement app/voice/live_api_client.py using google-genai SDK.
2. Implement app/voice/live_api_session.py for WebSocket lifecycle.
3. Implement app/voice/audio_manager.py for PCM audio I/O (16kHz in, 24kHz out).
4. Handle server-side interrupt detection (listen for 'interrupted' signal, clear buffer).
5. Add intent detection for voice transcripts (app/voice/intent_detector_voice.py).
6. Attach mock business tools to the Live API session.

### Approach B: TTS/STT/LLM Pipeline (Fallback)
1. Implement app/voice/stt.py with Deepgram/Whisper options.
2. Implement app/voice/tts.py with Gemini TTS/pyttsx3 options.
3. Implement app/voice/vad.py with WebRTC VAD.
4. Implement app/voice/pipeline_runner.py to orchestrate STT → ADK → TTS.
5. Add client-side interrupt handling (VAD cuts off TTS, restarts STT).

### Evaluation
1. Create evals/eval_scenarios_voice.json with 10+ voice scenarios.
2. Implement evals/voice_metrics.py (latency, interrupt accuracy, intent accuracy, WER, MOS).
3. Implement evals/run_eval_voice.py to benchmark both approaches.
4. Generate comparison reports.

### CLI Update
1. Update app/cli.py to support mode selection:
   [1] Text mode
   [2] Voice — Gemini Live API
   [3] Voice — TTS/STT Pipeline

Important:
- Keep voice code modular — system must run text-only if voice deps missing.
- Gemini Live API is primary. Pipeline is fallback and benchmark target.
- Handle interrupts for BOTH approaches.
- Add tests: tests/test_live_api.py, tests/test_interrupt_handler.py, tests/test_intent_detector.py.
```

---

## 34. Final Advice

Build this project in this order:

```text
Tools → Agents → CLI → Logs → Evals → Voice Live API → Voice Pipeline → Voice Evals → Simple UI → OpenAI SDK mirror
```

Do not start with voice.
Do not start with UI.
Do not start with deployment.

The core portfolio value is:

```text
Multi-agent orchestration + tool use + evaluation + voice-readiness (dual architecture with benchmarks)
```

That is enough to impress your company and also become a strong portfolio project.

---

## 35. Implementation Progress

### 2026-05-04 - Milestone 1: Repository Hygiene

Planned changes:

- Initialize the local repository on `main` and connect it to `https://github.com/htoothetnaung/adk-voice-support.git`.
- Add `.gitignore`, `.dockerignore`, `.env.example`, and `README.md`.
- Keep secrets, local environments, generated logs, evaluation reports, audio artifacts, and IDE files out of Git.

Status:

- Completed and pushed in commit `ea58809`.

### 2026-05-04 - Milestone 2: Python Foundation

Planned changes:

- Add `pyproject.toml`, package directories, config loader, mock data, deterministic mock tools, and tracked `.gitkeep` placeholders for runtime output directories.
- Keep the implementation text-only and API-free.

Status:

- Completed and pushed in commit `ae3ce8a`.

### 2026-05-04 - Milestone 3: Tool Tests and Docs

Planned changes:

- Add focused pytest coverage for every Phase 1 mock tool.
- Update README usage notes for the current deterministic, API-free phase.
- Run `python -m pytest` before the final Phase 1 commit and push.

Status:

- Completed with `python -m pytest` passing 15 tests.

### 2026-05-04 - Milestone 4: ADK Agents, CLI, and Text Runner

Completed changes:

- Added ADK-compatible root and specialist agent definitions for ADK Web discovery.
- Added deterministic `SupportAgentRunner` for local CLI, tests, and evals without API calls.
- Added intent detection, structured response objects, JSON trace logging, and interactive `python -m app.cli` text mode.
- Added tests for root agent discovery and routing behavior.

Validation:

- `python -m pytest` passed 20 tests.

### 2026-05-04 - Milestone 5: Text Evaluation Lab

Completed changes:

- Added text evaluation scenarios, metrics, and `python -m evals.run_eval`.
- Added JSON report generation under `evals/reports/`.
- Added tests for evaluation metrics and scenario execution.
- Tightened policy search so topic matches outrank common-word matches.

Validation:

- `python -m pytest` passed 27 tests.
- `python -m evals.run_eval` passed 12/12 scenarios.

### 2026-05-04 - Milestone 6: Voice Architecture and Voice Evaluation

Completed changes:

- Added transcript-driven Gemini Live API simulation and TTS/STT pipeline simulation.
- Added voice intent normalization, audio buffer helpers, interrupt handling, STT/TTS/VAD provider boundaries, and voice CLI modes.
- Added 10 voice scenarios, voice metrics, WER calculation, and `python -m evals.run_eval_voice --approach both --compare`.
- Added tests for voice intent detection, interrupt handling, Live API simulation, and voice evals.

Validation:

- `python -m pytest` passed 38 tests.
- `python -m evals.run_eval` passed 12/12 scenarios.
- `python -m evals.run_eval_voice --approach both --compare` passed 10/10 Live API simulation and 10/10 pipeline simulation scenarios.

Current limitation:

- Voice modes are transcript-driven simulations by default. Real microphone/audio streaming and provider calls require API keys, provider packages, and the next integration hardening pass.

### 2026-05-04 - Milestone 7: Documentation and Optional UI Entrypoints

Completed changes:

- Updated README with runnable commands and current feature status.
- Added architecture, evaluation, voice architecture, and OpenAI Agents SDK mirror docs.
- Added optional Streamlit and Gradio entrypoints with dependency guards.

Validation:

- `python -m pytest` passed 38 tests.
- `python -m evals.run_eval` passed 12/12 scenarios.
- `python -m evals.run_eval_voice --approach both --compare` passed 10/10 Live API simulation and 10/10 pipeline simulation scenarios.

### 2026-05-04 - Milestone 8: uv Environment Setup

Completed changes:

- Created repo-local `.venv` with `uv` using Python 3.13.9.
- Installed project and dev dependencies into `.venv`.
- Generated `uv.lock` for reproducible dependency resolution.
- Updated README with uv setup, run, test, text eval, voice eval, and CLI commands.
- Fixed setuptools package discovery to include only `app*` and `evals*`.

Validation:

- `.venv\Scripts\python.exe -m pytest` passed 38 tests.
- `.venv\Scripts\python.exe -m evals.run_eval` passed 12/12 scenarios.
- `.venv\Scripts\python.exe -m evals.run_eval_voice --approach both --compare` passed 10/10 Live API simulation and 10/10 pipeline simulation scenarios.
- `uv run python -m pytest` passed 38 tests.
