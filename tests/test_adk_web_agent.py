import asyncio

from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService
from google.genai import types

from adk_agents.voice_support.agent import root_agent


def test_adk_web_agent_emits_tool_and_final_events() -> None:
    async def run() -> list:
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name="voice_support",
            user_id="tester",
            session_id="adk_web_test",
        )
        ctx = InvocationContext(
            session_service=session_service,
            invocation_id="invocation_test",
            agent=root_agent,
            user_content=types.Content(
                role="user",
                parts=[types.Part(text="I was charged twice. My email is alice@example.com.")],
            ),
            session=session,
        )

        return [event async for event in root_agent._run_async_impl(ctx)]

    events = asyncio.run(run())

    assert len(events) >= 3
    assert any(event.content and event.content.parts[0].function_call for event in events)
    assert any(event.content and event.content.parts[0].function_response for event in events)
    final_event = events[-1]
    assert final_event.turn_complete is True
    assert "refund ticket" in final_event.content.parts[0].text
    assert final_event.custom_metadata["selected_agent"] == "billing_agent"
