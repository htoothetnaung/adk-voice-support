"""Human handoff and escalation tools."""

from __future__ import annotations

from hashlib import sha256


def summarize_conversation_for_human(conversation: list[dict]) -> dict:
    """Create structured human handoff summary."""

    user_messages = [turn.get("content", "") for turn in conversation if turn.get("role") == "user"]
    assistant_messages = [turn.get("content", "") for turn in conversation if turn.get("role") == "assistant"]
    latest_user_message = user_messages[-1] if user_messages else ""

    return {
        "summary": latest_user_message or "No user message provided.",
        "user_message_count": len(user_messages),
        "assistant_message_count": len(assistant_messages),
        "conversation_turns": len(conversation),
    }


def create_escalation_ticket(summary: str, urgency: str = "medium") -> dict:
    """Create mock escalation ticket."""

    normalized_urgency = urgency if urgency in {"low", "medium", "high"} else "medium"
    digest = sha256(summary.encode("utf-8")).hexdigest()[:10]
    return {
        "created": True,
        "ticket_id": f"esc_{normalized_urgency}_{digest}",
        "ticket_type": "escalation",
        "summary": summary,
        "urgency": normalized_urgency,
        "status": "open",
    }
