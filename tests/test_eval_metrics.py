from evals.metrics import forbidden_phrase_violation, phrase_coverage, routing_correct, scenario_passed, tool_recall


def test_routing_correct() -> None:
    assert routing_correct("billing_agent", "billing_agent") is True
    assert routing_correct("billing_agent", "policy_agent") is False


def test_tool_recall() -> None:
    assert tool_recall(["lookup_customer", "lookup_invoice"], ["lookup_customer"]) == 0.5
    assert tool_recall([], []) == 1.0


def test_phrase_coverage() -> None:
    assert phrase_coverage(["refund", "ticket"], "Created a refund ticket.") == 1.0
    assert phrase_coverage(["refund", "ticket"], "Created a ticket.") == 0.5


def test_forbidden_phrase_violation() -> None:
    assert forbidden_phrase_violation(["guaranteed"], "This is guaranteed.") is True
    assert forbidden_phrase_violation(["guaranteed"], "This needs review.") is False


def test_scenario_passed() -> None:
    result = {
        "routing_correct": True,
        "intent_correct": True,
        "tool_recall": 1.0,
        "required_phrase_coverage": 1.0,
        "forbidden_phrase_violation": False,
        "latency_ms": 10,
        "max_latency_ms": 100,
    }

    assert scenario_passed(result) is True

