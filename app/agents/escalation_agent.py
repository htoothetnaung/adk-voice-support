"""Human escalation ADK agent."""

from google.adk.agents import Agent

from app.agents.prompts import ESCALATION_INSTRUCTION
from app.config import settings
from app.tools import create_escalation_ticket, summarize_conversation_for_human

human_escalation_agent = Agent(
    name="human_escalation_agent",
    model=settings.adk_model,
    description="Creates structured handoff summaries and escalation tickets for humans.",
    instruction=ESCALATION_INSTRUCTION,
    tools=[summarize_conversation_for_human, create_escalation_ticket],
)

