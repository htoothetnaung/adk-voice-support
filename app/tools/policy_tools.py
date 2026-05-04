"""Policy lookup tools."""

from __future__ import annotations

from app.data.mock_policies import POLICIES


def search_policy_knowledge_base(query: str) -> dict:
    """Search mock policy documents."""

    normalized_query = query.strip().lower()
    if not normalized_query:
        return {"found": False, "matches": []}

    matches = []
    for topic, policy_text in POLICIES.items():
        if topic in normalized_query or any(word in policy_text.lower() for word in normalized_query.split()):
            matches.append({"topic": topic, "text": policy_text})

    return {"found": bool(matches), "matches": matches}

