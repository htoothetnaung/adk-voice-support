"""Support agent runtime.

The repo exposes ADK `Agent` objects for ADK Web compatibility, while this
runner provides deterministic local execution for CLI, tests, and evals.
"""

from __future__ import annotations

import re
import time

from app.services.intent_detector import IntentDetector
from app.services.response_parser import SupportResponse
from app.tools import (
    check_refund_eligibility,
    create_escalation_ticket,
    create_refund_ticket,
    create_support_ticket,
    get_known_issues,
    lookup_customer,
    lookup_invoice,
    run_basic_diagnostic,
    search_policy_knowledge_base,
    summarize_conversation_for_human,
)


class SupportAgentRunner:
    """Run support requests through deterministic routing and mock tools."""

    def __init__(self, intent_detector: IntentDetector | None = None) -> None:
        self.intent_detector = intent_detector or IntentDetector()
        self.conversation: list[dict] = []

    def run(self, user_message: str) -> SupportResponse:
        """Route a user message and return a structured support response."""

        started = time.perf_counter()
        self.conversation.append({"role": "user", "content": user_message})
        intent_result = self.intent_detector.detect(user_message, self.conversation)
        intent = intent_result["intent"]

        if intent in {"billing_issue", "refund_request"}:
            response = self._handle_billing(user_message, intent)
        elif intent == "technical_issue":
            response = self._handle_technical(user_message, intent)
        elif intent == "policy_question":
            response = self._handle_policy(user_message, intent)
        elif intent == "human_escalation":
            response = self._handle_escalation(user_message, intent)
        else:
            response = SupportResponse(
                user_message=user_message,
                final_response="I can help, but I need one more detail. Is this about billing, a technical issue, a policy question, or speaking with a human?",
                intent=intent,
                selected_agent="support_triage_agent",
                raw_events=[intent_result],
            )

        response.latency_ms = int((time.perf_counter() - started) * 1000)
        response.raw_events.insert(0, {"event": "intent_detected", **intent_result})
        self.conversation.append({"role": "assistant", "content": response.final_response})
        return response

    def _handle_billing(self, user_message: str, intent: str) -> SupportResponse:
        email = self._extract_email(user_message)
        customer_id = self._extract_customer_id(user_message)
        invoice_id = self._extract_invoice_id(user_message)
        tool_calls = []

        customer_result = lookup_customer(customer_id=customer_id, email=email)
        tool_calls.append({"name": "lookup_customer", "result": customer_result})
        customer = customer_result.get("customer") if customer_result.get("found") else None

        invoice_result = lookup_invoice(invoice_id=invoice_id, customer_id=customer["customer_id"] if customer else customer_id)
        tool_calls.append({"name": "lookup_invoice", "result": invoice_result})

        invoice = invoice_result.get("invoice")
        if not invoice and invoice_result.get("invoices"):
            invoice = invoice_result["invoices"][0]

        if not customer:
            final = "I can help with the billing issue. Please share your customer ID or account email so I can look up the account."
        elif not invoice:
            ticket = create_support_ticket(customer["customer_id"], "billing", "Billing issue needs invoice review.")
            tool_calls.append({"name": "create_support_ticket", "result": ticket})
            final = f"I found your account, but I could not confirm the invoice. I created support ticket {ticket['ticket_id']} for billing review."
        else:
            eligibility = check_refund_eligibility(invoice["invoice_id"])
            tool_calls.append({"name": "check_refund_eligibility", "result": eligibility})
            if eligibility["eligible"]:
                ticket = create_refund_ticket(customer["customer_id"], invoice["invoice_id"], eligibility["reason"])
                tool_calls.append({"name": "create_refund_ticket", "result": ticket})
                final = f"I found a {eligibility['reason']} on invoice {invoice['invoice_id']}. I created refund ticket {ticket['ticket_id']} for the billing team."
            else:
                ticket = create_support_ticket(customer["customer_id"], "billing", eligibility["reason"])
                tool_calls.append({"name": "create_support_ticket", "result": ticket})
                final = f"Invoice {invoice['invoice_id']} is not automatically refund eligible because it is {eligibility['reason']}. I created ticket {ticket['ticket_id']} for review."

        return SupportResponse(
            user_message=user_message,
            final_response=final,
            intent=intent,
            selected_agent="billing_agent",
            tool_calls=tool_calls,
        )

    def _handle_technical(self, user_message: str, intent: str) -> SupportResponse:
        email = self._extract_email(user_message)
        customer_id = self._extract_customer_id(user_message)
        issue_type = self._detect_issue_type(user_message)
        tool_calls = []

        customer_result = lookup_customer(customer_id=customer_id, email=email)
        tool_calls.append({"name": "lookup_customer", "result": customer_result})
        known_issues = get_known_issues(issue_type)
        tool_calls.append({"name": "get_known_issues", "result": known_issues})
        diagnostic = run_basic_diagnostic(customer_id, issue_type)
        tool_calls.append({"name": "run_basic_diagnostic", "result": diagnostic})

        ticket = create_support_ticket(
            customer_id if customer_id else customer_result.get("customer", {}).get("customer_id"),
            issue_type,
            diagnostic["detail"],
        )
        tool_calls.append({"name": "create_support_ticket", "result": ticket})

        final = f"I ran a {issue_type} diagnostic: {diagnostic['detail']} I created support ticket {ticket['ticket_id']} so support can track the next step."
        return SupportResponse(
            user_message=user_message,
            final_response=final,
            intent=intent,
            selected_agent="technical_support_agent",
            tool_calls=tool_calls,
        )

    def _handle_policy(self, user_message: str, intent: str) -> SupportResponse:
        policy_result = search_policy_knowledge_base(user_message)
        tool_calls = [{"name": "search_policy_knowledge_base", "result": policy_result}]

        if policy_result["found"]:
            match = policy_result["matches"][0]
            final = f"Here is the {match['topic']} policy from our knowledge base: {match['text']}"
        else:
            final = "I could not confirm that policy in the mock knowledge base. I should escalate this to a human for confirmation."

        return SupportResponse(
            user_message=user_message,
            final_response=final,
            intent=intent,
            selected_agent="policy_agent",
            tool_calls=tool_calls,
        )

    def _handle_escalation(self, user_message: str, intent: str) -> SupportResponse:
        summary = summarize_conversation_for_human(self.conversation)
        ticket = create_escalation_ticket(summary["summary"], urgency="high" if self._is_urgent(user_message) else "medium")
        tool_calls = [
            {"name": "summarize_conversation_for_human", "result": summary},
            {"name": "create_escalation_ticket", "result": ticket},
        ]
        final = f"I understand. I created escalation ticket {ticket['ticket_id']} and included a summary for a human support representative."
        return SupportResponse(
            user_message=user_message,
            final_response=final,
            intent=intent,
            selected_agent="human_escalation_agent",
            tool_calls=tool_calls,
        )

    @staticmethod
    def _extract_email(text: str) -> str | None:
        match = re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", text)
        return match.group(0).lower() if match else None

    @staticmethod
    def _extract_customer_id(text: str) -> str | None:
        match = re.search(r"\bcust_\d+\b", text, re.IGNORECASE)
        return match.group(0).lower() if match else None

    @staticmethod
    def _extract_invoice_id(text: str) -> str | None:
        match = re.search(r"\binv_\d+\b", text, re.IGNORECASE)
        return match.group(0).lower() if match else None

    @staticmethod
    def _detect_issue_type(text: str) -> str:
        lowered = text.lower()
        if any(term in lowered for term in ["otp", "login", "log in", "password"]):
            return "login"
        if any(term in lowered for term in ["app", "crash", "mobile"]):
            return "mobile_app"
        if any(term in lowered for term in ["integration", "webhook"]):
            return "integration"
        return "general"

    @staticmethod
    def _is_urgent(text: str) -> bool:
        lowered = text.lower()
        return any(term in lowered for term in ["unacceptable", "legal", "lawyer", "complaint", "angry"])

