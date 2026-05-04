"""Policy lookup tools."""

from __future__ import annotations

from app.data.mock_policies import POLICIES

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "do",
    "how",
    "is",
    "long",
    "my",
    "the",
    "what",
    "you",
    "your",
}


def search_policy_knowledge_base(query: str) -> dict:
    """Search mock policy documents."""

    normalized_query = query.strip().lower()
    if not normalized_query:
        return {"found": False, "matches": []}

    topic_matches = [
        {"topic": topic, "text": policy_text}
        for topic, policy_text in POLICIES.items()
        if topic in normalized_query
    ]
    if topic_matches:
        return {"found": True, "matches": topic_matches}

    query_terms = [word for word in normalized_query.split() if word not in STOPWORDS and len(word) > 2]
    matches = []
    for topic, policy_text in POLICIES.items():
        if any(word in policy_text.lower() for word in query_terms):
            matches.append({"topic": topic, "text": policy_text})

    return {"found": bool(matches), "matches": matches}
