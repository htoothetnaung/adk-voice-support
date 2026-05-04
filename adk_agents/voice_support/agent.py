"""Offline-safe ADK Web agent.

ADK Web discovers agents from `<agents_dir>/<agent_name>/agent.py`. This file
keeps that native discovery path working while delegating behavior to the same
deterministic support backend used by the CLI, evals, Gradio, and browser demo.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types
from pydantic import PrivateAttr

from app.services import SupportAgentRunner


class OfflineSupportAgent(BaseAgent):
    """ADK custom agent that works in ADK Web without external model keys."""

    _runner: SupportAgentRunner = PrivateAttr(default_factory=SupportAgentRunner)

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Run one ADK text turn and emit transparent response/tool events."""

        user_text = _extract_user_text(ctx)
        response = self._runner.run(user_text)

        for index, tool_call in enumerate(response.tool_calls):
            call_id = f"tool_{index}_{tool_call['name']}"
            yield Event(
                author=self.name,
                invocationId=ctx.invocation_id,
                content=types.Content(
                    role="model",
                    parts=[
                        types.Part(
                            functionCall=types.FunctionCall(
                                id=call_id,
                                name=tool_call["name"],
                                args={},
                            )
                        )
                    ],
                ),
                customMetadata={
                    "selected_agent": response.selected_agent,
                    "intent": response.intent,
                    "tool_name": tool_call["name"],
                },
            )
            yield Event(
                author=self.name,
                invocationId=ctx.invocation_id,
                content=types.Content(
                    role="tool",
                    parts=[
                        types.Part(
                            functionResponse=types.FunctionResponse(
                                id=call_id,
                                name=tool_call["name"],
                                response=tool_call["result"],
                            )
                        )
                    ],
                ),
            )

        yield Event(
            author=self.name,
            invocationId=ctx.invocation_id,
            content=types.Content(
                role="model",
                parts=[types.Part(text=response.final_response)],
            ),
            turnComplete=True,
            customMetadata={
                "selected_agent": response.selected_agent,
                "intent": response.intent,
                "tools": [tool_call["name"] for tool_call in response.tool_calls],
                "latency_ms": response.latency_ms,
            },
        )


def _extract_user_text(ctx: InvocationContext) -> str:
    if not ctx.user_content or not ctx.user_content.parts:
        return ""
    return " ".join(part.text for part in ctx.user_content.parts if getattr(part, "text", None)).strip()


root_agent = OfflineSupportAgent(
    name="voice_support_offline_agent",
    description="Offline-safe ADK Web agent for the voice support simulator.",
)

