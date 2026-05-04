# OpenAI Agents SDK Mirror Plan

This project is intentionally designed so the same system can later be rebuilt with OpenAI Agents SDK.

Keep these concepts framework-neutral:

- agent names
- tool names
- evaluation scenarios
- mock data
- metrics
- CLI behavior
- UI behavior
- voice approach abstraction

Only the agent runtime implementation should change.

| Feature | Google ADK | OpenAI Agents SDK | Notes |
|---|---|---|---|
| Agent creation | Implemented as ADK `Agent` definitions | TBD | Keep prompts and names reusable |
| Sub-agent/handoff | ADK root with specialists | TBD | Deterministic runner currently handles route |
| Tool calling | Mock Python functions | TBD | Tool contracts are framework-neutral |
| Evaluation | Custom JSON runner | Reuse | Same scenarios should run against both |
| Voice support | Transcript-driven simulation | TBD | Keep Live vs Pipeline abstraction |
| Debugging | JSON traces and eval reports | Reuse | Add richer traces later |

