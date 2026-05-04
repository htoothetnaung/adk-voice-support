# Voice Support ADK Lab

ADK-first multi-agent customer support simulator and evaluation lab.

This repository is starting with a deterministic Python foundation: mock data, mock business tools, and tests. Google ADK agents, CLI routing, evaluation runs, voice support, and the later OpenAI Agents SDK mirror will be added in later milestones.

## Current Phase

Phase 1: repository hygiene, Python package structure, configuration, mock tools, and tests.

Implemented in this phase:

- Safe `.gitignore` and `.dockerignore`
- `.env.example` with placeholder values only
- Environment-driven config loader
- Mock customer, invoice, policy, and known-issue data
- Deterministic mock tools for billing, technical support, policy lookup, and escalation
- Focused pytest coverage for the tool layer

## Planned Architecture

- Root triage agent
- Billing, technical support, policy, and human escalation specialists
- Mock customer, invoice, policy, known-issue, ticket, and escalation tools
- Text CLI first
- Evaluation lab before UI
- Voice layer after text evaluation works

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Create a local `.env` from `.env.example` when real API-backed phases begin. Do not commit `.env`.

## Test

```powershell
python -m pytest
```

The current tests do not call Google ADK, Gemini, Deepgram, ElevenLabs, or any other external service.

## Roadmap

1. Mock tools and tests
2. Google ADK agents and CLI
3. Evaluation lab
4. Gemini Live API voice approach
5. TTS/STT/LLM fallback pipeline
6. Voice benchmarks
7. OpenAI Agents SDK mirror
