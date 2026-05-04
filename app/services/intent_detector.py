"""Deterministic text intent detection for routing and evaluation."""

from __future__ import annotations

import re


class IntentDetector:
    """Classify support utterances into the project intents."""

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

    _PATTERNS = {
        "human_escalation": r"\b(human|person|agent|manager|supervisor|complaint|unacceptable|legal|lawyer)\b",
        "refund_request": r"\b(refund|money back|reimburse|charged twice|duplicate charge)\b",
        "billing_issue": r"\b(billing|invoice|charged|charge|payment|subscription|cancel subscription|paid)\b",
        "technical_issue": r"\b(login|log in|otp|crash|crashing|error|bug|integration|webhook|not working|app)\b",
        "policy_question": r"\b(policy|privacy|terms|warranty|cancel anytime|cancellation|data|store)\b",
        "order_status": r"\b(order|shipment|shipping|delivery|tracking)\b",
        "account_issue": r"\b(account|profile|email|password|locked)\b",
    }

    def detect(self, text: str, context: list[dict] | None = None) -> dict:
        """
        Return an intent classification dictionary.

        The current implementation is deterministic and keyword-based so CLI and
        tests work without model/API calls. A later phase can add LLM fallback.
        """

        del context
        normalized = re.sub(r"\s+", " ", text.strip().lower())
        if not normalized:
            return {"intent": "unknown", "confidence": 0.0, "method": "keyword", "raw_text": text}

        for intent, pattern in self._PATTERNS.items():
            if re.search(pattern, normalized):
                return {"intent": intent, "confidence": 0.9, "method": "keyword", "raw_text": text}

        return {"intent": "unknown", "confidence": 0.25, "method": "keyword", "raw_text": text}
