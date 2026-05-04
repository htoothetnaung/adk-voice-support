"""Billing ADK agent."""

from google.adk.agents import Agent

from app.agents.prompts import BILLING_INSTRUCTION
from app.config import settings
from app.tools import check_refund_eligibility, create_refund_ticket, create_support_ticket, lookup_customer, lookup_invoice

billing_agent = Agent(
    name="billing_agent",
    model=settings.adk_model,
    description="Handles billing, invoices, refunds, charges, and subscriptions.",
    instruction=BILLING_INSTRUCTION,
    tools=[
        lookup_customer,
        lookup_invoice,
        check_refund_eligibility,
        create_refund_ticket,
        create_support_ticket,
    ],
)

