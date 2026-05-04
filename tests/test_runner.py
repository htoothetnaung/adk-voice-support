from app.services import SupportAgentRunner


def tool_names(response) -> list[str]:
    return [call["name"] for call in response.tool_calls]


def test_runner_routes_duplicate_charge_to_billing() -> None:
    response = SupportAgentRunner().run("I was charged twice this month. My email is alice@example.com.")

    assert response.intent == "refund_request"
    assert response.selected_agent == "billing_agent"
    assert "create_refund_ticket" in tool_names(response)
    assert "refund ticket" in response.final_response


def test_runner_routes_login_issue_to_technical_support() -> None:
    response = SupportAgentRunner().run("I cannot log in to my account.")

    assert response.intent == "technical_issue"
    assert response.selected_agent == "technical_support_agent"
    assert "run_basic_diagnostic" in tool_names(response)


def test_runner_routes_cancellation_policy() -> None:
    response = SupportAgentRunner().run("What is your cancellation policy?")

    assert response.intent == "policy_question"
    assert response.selected_agent == "policy_agent"
    assert "cancel anytime" in response.final_response


def test_runner_routes_human_escalation() -> None:
    response = SupportAgentRunner().run("This is unacceptable. I want to talk to a human.")

    assert response.intent == "human_escalation"
    assert response.selected_agent == "human_escalation_agent"
    assert "create_escalation_ticket" in tool_names(response)

