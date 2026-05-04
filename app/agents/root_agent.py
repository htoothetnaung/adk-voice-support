"""Root ADK agent discoverable by ADK Web."""

from google.adk.agents import Agent

from app.agents.billing_agent import billing_agent
from app.agents.escalation_agent import human_escalation_agent
from app.agents.policy_agent import policy_agent
from app.agents.prompts import ROOT_TRIAGE_INSTRUCTION
from app.agents.technical_support_agent import technical_support_agent
from app.config import settings

root_agent = Agent(
    name="support_triage_agent",
    model=settings.adk_model,
    description="Routes customer support requests to the correct specialist agent.",
    instruction=ROOT_TRIAGE_INSTRUCTION,
    sub_agents=[
        billing_agent,
        technical_support_agent,
        policy_agent,
        human_escalation_agent,
    ],
)

