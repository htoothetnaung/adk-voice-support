from app.agents.root_agent import root_agent


def test_root_agent_is_discoverable() -> None:
    assert root_agent.name == "support_triage_agent"
    assert {agent.name for agent in root_agent.sub_agents} == {
        "billing_agent",
        "technical_support_agent",
        "policy_agent",
        "human_escalation_agent",
    }

