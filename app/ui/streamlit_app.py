"""Optional Streamlit UI for the simulator."""

from __future__ import annotations

from app.services import SupportAgentRunner


def main() -> None:
    """Run a minimal Streamlit chat UI."""

    try:
        import streamlit as st
    except ImportError as exc:  # pragma: no cover - optional UI dependency.
        raise RuntimeError("Install streamlit to run this UI: python -m pip install streamlit") from exc

    st.set_page_config(page_title="Voice Support ADK Lab", layout="wide")
    st.title("Voice Support ADK Lab")

    if "runner" not in st.session_state:
        st.session_state.runner = SupportAgentRunner()
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_message = st.chat_input("Customer message")
    if user_message:
        st.session_state.messages.append({"role": "user", "content": user_message})
        response = st.session_state.runner.run(user_message)
        st.session_state.messages.append({"role": "assistant", "content": response.final_response})
        st.rerun()


if __name__ == "__main__":
    main()

