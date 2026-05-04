"""Technical support ADK agent."""

from google.adk.agents import Agent

from app.agents.prompts import TECHNICAL_SUPPORT_INSTRUCTION
from app.config import settings
from app.tools import create_support_ticket, get_known_issues, lookup_customer, run_basic_diagnostic

technical_support_agent = Agent(
    name="technical_support_agent",
    model=settings.adk_model,
    description="Handles login, app, integration, OTP, and product reliability issues.",
    instruction=TECHNICAL_SUPPORT_INSTRUCTION,
    tools=[lookup_customer, get_known_issues, run_basic_diagnostic, create_support_ticket],
)

