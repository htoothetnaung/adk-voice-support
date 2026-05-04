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

