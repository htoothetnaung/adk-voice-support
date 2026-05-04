"""Shared response structures for the deterministic runner."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class SupportResponse:
    """Structured response returned by CLI, evals, and future transports."""

    user_message: str
    final_response: str
    intent: str
    selected_agent: str
    tool_calls: list[dict] = field(default_factory=list)
    latency_ms: int = 0
    raw_events: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert the response to a JSON-serializable dictionary."""

        return asdict(self)

