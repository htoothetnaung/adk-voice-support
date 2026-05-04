"""Policy ADK agent."""

from google.adk.agents import Agent

from app.agents.prompts import POLICY_INSTRUCTION
from app.config import settings
from app.tools import search_policy_knowledge_base

policy_agent = Agent(
    name="policy_agent",
    model=settings.adk_model,
    description="Answers policy, FAQ, warranty, privacy, cancellation, and refund-rule questions.",
    instruction=POLICY_INSTRUCTION,
    tools=[search_policy_knowledge_base],
)

