"""Technical support tools."""

from __future__ import annotations

from app.data.mock_known_issues import KNOWN_ISSUES


def get_known_issues(product_area: str | None = None) -> dict:
    """Return mock known technical issues."""

    if product_area:
        normalized_area = product_area.strip().lower()
        issue = KNOWN_ISSUES.get(normalized_area)
        if issue:
            return {"found": True, "issues": [dict(issue)]}
        return {"found": False, "issues": []}

    return {"found": True, "issues": [dict(issue) for issue in KNOWN_ISSUES.values()]}


def run_basic_diagnostic(customer_id: str | None, issue_type: str) -> dict:
    """Run mock diagnostic for a technical issue."""

    normalized_issue = issue_type.strip().lower()
    checks = {
        "login": {"result": "warning", "detail": "Recent OTP delivery delays detected."},
        "mobile_app": {"result": "pass", "detail": "No account-specific mobile outage detected."},
        "integration": {"result": "warning", "detail": "Webhook retries are delayed for this account segment."},
    }
    diagnostic = checks.get(normalized_issue, {"result": "unknown", "detail": "No diagnostic rule matched."})

    return {
        "customer_id": customer_id,
        "issue_type": normalized_issue,
        "result": diagnostic["result"],
        "detail": diagnostic["detail"],
    }


def create_support_ticket(customer_id: str | None, issue_type: str, summary: str) -> dict:
    """Create a generic mock support ticket."""

    customer_part = customer_id or "unknown_customer"
    normalized_issue = issue_type.strip().lower().replace(" ", "_")
    return {
        "created": True,
        "ticket_id": f"support_{customer_part}_{normalized_issue}",
        "ticket_type": "support",
        "customer_id": customer_id,
        "issue_type": issue_type,
        "summary": summary,
        "status": "open",
    }

