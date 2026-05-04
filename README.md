# Voice Support ADK Lab

ADK-first multi-agent customer support simulator and evaluation lab.

This repository contains a runnable ADK-first customer support simulator with deterministic local execution, mock tools, text evaluation, transcript-driven voice simulation, and voice evaluation.

## Current Phase

Implemented:

Implemented in this phase:

- Safe `.gitignore` and `.dockerignore`
- `.env.example` with placeholder values only
- Environment-driven config loader
- ADK-compatible root and specialist agent definitions
- Deterministic local runner for CLI, tests, and evals
- Mock customer, invoice, policy, and known-issue data
- Mock tools for billing, technical support, policy lookup, and escalation
- Text evaluation runner and JSON reports
- Transcript-driven Gemini Live API and TTS/STT pipeline simulations
- Voice evaluation runner and JSON reports
- Focused pytest coverage

## Planned Architecture

- Root triage agent
- Billing, technical support, policy, and human escalation specialists
- Mock customer, invoice, policy, known-issue, ticket, and escalation tools
- Text CLI first
- Evaluation lab before UI
- Voice layer after text evaluation works

## Setup

```powershell
uv venv .venv --python C:\Users\austin\anaconda3\python.exe
uv sync --extra dev
.venv\Scripts\Activate.ps1
```

Create a local `.env` from `.env.example` when real API-backed phases begin. Do not commit `.env`.

If `.venv` already exists, use:

```powershell
uv sync --extra dev
```

## Test

```powershell
uv run python -m pytest
```

The current tests do not call Google ADK, Gemini, Deepgram, ElevenLabs, or any other external service.

## Run CLI

```powershell
uv run python -m app.cli
```

Modes:

- `[1]` Text mode
- `[2]` Gemini Live API simulation using typed transcripts
- `[3]` TTS/STT pipeline simulation using typed transcripts

## Run Evaluation

```powershell
uv run python -m evals.run_eval
uv run python -m evals.run_eval_voice --approach both --compare
```

Reports are written under `evals/reports/` and are intentionally ignored by Git.

## Quick Start

From a fresh clone on this machine:

```powershell
cd C:\Users\austin\Documents\Brillar_job\voice\adk_voice_support
uv sync --extra dev
uv run python -m pytest
uv run python -m evals.run_eval
uv run python -m evals.run_eval_voice --approach both --compare
uv run python -m app.cli
```

## Run ADK Web

The ADK root agent is exposed as `app.agents.root_agent.root_agent`. Use the installed ADK tooling for your environment and point it at this package/module.

## Voice Layer

The current voice layer is intentionally offline-safe:

- Gemini Live API mode is represented by a session/client boundary plus transcript-driven simulation.
- Pipeline mode is represented by STT, TTS, VAD, audio buffer, and interrupt boundaries plus transcript-driven simulation.
- Real microphone streaming and provider calls require API keys and a follow-up provider integration pass.

## Roadmap

1. Mock tools and tests
2. Google ADK agents and CLI
3. Evaluation lab
4. Gemini Live API voice approach
5. TTS/STT/LLM fallback pipeline
6. Voice benchmarks
7. OpenAI Agents SDK mirror
