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


def test_lookup_customer_by_email() -> None:
    result = lookup_customer(email="alice@example.com")

    assert result["found"] is True
    assert result["customer"]["customer_id"] == "cust_001"
    assert result["customer"]["plan"] == "Pro"


def test_lookup_customer_by_id() -> None:
    result = lookup_customer(customer_id="cust_002")

    assert result["found"] is True
    assert result["customer"]["email"] == "minthu@example.com"


def test_lookup_customer_requires_identifier() -> None:
    result = lookup_customer()

    assert result["found"] is False
    assert "required" in result["error"]


def test_lookup_invoice_by_invoice_id() -> None:
    result = lookup_invoice(invoice_id="inv_1001")

    assert result["found"] is True
    assert result["invoice"]["customer_id"] == "cust_001"
    assert result["invoice"]["duplicate_charge"] is True


def test_lookup_invoice_by_customer_id() -> None:
    result = lookup_invoice(customer_id="cust_002")

    assert result["found"] is True
    assert result["invoices"][0]["invoice_id"] == "inv_1002"


def test_refund_eligibility_for_duplicate_charge() -> None:
    result = check_refund_eligibility("inv_1001")

    assert result["eligible"] is True
    assert result["reason"] == "duplicate charge detected"


def test_refund_eligibility_rejects_old_invoice() -> None:
    result = check_refund_eligibility("inv_1002")

    assert result["eligible"] is False
    assert result["reason"] == "outside 14-day refund window"


def test_create_refund_ticket() -> None:
    result = create_refund_ticket("cust_001", "inv_1001", "duplicate charge")

    assert result["created"] is True
    assert result["ticket_id"] == "refund_cust_001_inv_1001"
    assert result["ticket_type"] == "refund"


def test_get_known_issues_for_product_area() -> None:
    result = get_known_issues("login")

    assert result["found"] is True
    assert result["issues"][0]["product_area"] == "login"
    assert result["issues"][0]["status"] == "investigating"


def test_run_basic_diagnostic() -> None:
    result = run_basic_diagnostic("cust_001", "login")

    assert result["customer_id"] == "cust_001"
    assert result["issue_type"] == "login"
    assert result["result"] == "warning"


def test_create_support_ticket() -> None:
    result = create_support_ticket("cust_001", "login", "Customer cannot receive OTP.")

    assert result["created"] is True
    assert result["ticket_id"] == "support_cust_001_login"
    assert result["summary"] == "Customer cannot receive OTP."


def test_search_policy_knowledge_base() -> None:
    result = search_policy_knowledge_base("refund policy")

    assert result["found"] is True
    assert result["matches"][0]["topic"] == "refund"
    assert "14 days" in result["matches"][0]["text"]


def test_summarize_conversation_for_human() -> None:
    conversation = [
        {"role": "user", "content": "I was charged twice."},
        {"role": "assistant", "content": "I can help with that."},
        {"role": "user", "content": "I want a human now."},
    ]

    result = summarize_conversation_for_human(conversation)

    assert result["summary"] == "I want a human now."
    assert result["user_message_count"] == 2
    assert result["assistant_message_count"] == 1
    assert result["conversation_turns"] == 3


def test_create_escalation_ticket_is_deterministic() -> None:
    first = create_escalation_ticket("Customer requested human support.", urgency="high")
    second = create_escalation_ticket("Customer requested human support.", urgency="high")

    assert first == second
    assert first["created"] is True
    assert first["ticket_id"].startswith("esc_high_")
    assert first["urgency"] == "high"


def test_create_escalation_ticket_normalizes_unknown_urgency() -> None:
    result = create_escalation_ticket("Customer is upset.", urgency="critical")

    assert result["urgency"] == "medium"

