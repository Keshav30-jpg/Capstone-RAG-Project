import os
import time
import streamlit as st

DEFAULT_KEY_QUESTION_LIMIT = 10
WINDOW_SECONDS = 4 * 60 * 60  


def init_key_state() -> None:
    """
    Set up session_state defaults. Call this once at the top of app.py,
    before anything else touches these keys.
    """
    if "key_mode" not in st.session_state:
        st.session_state.key_mode = "default"  
    if "user_api_key" not in st.session_state:
        st.session_state.user_api_key = "" 
    if "questions_asked" not in st.session_state:
        st.session_state.questions_asked = 0
    if "window_start_time" not in st.session_state:
        st.session_state.window_start_time = time.time()


def _maybe_reset_window() -> None:
    
    elapsed = time.time() - st.session_state.window_start_time
    if elapsed > WINDOW_SECONDS:
        st.session_state.questions_asked = 0
        st.session_state.window_start_time = time.time()


def get_active_api_key() -> str:
    
    if st.session_state.key_mode == "own" and st.session_state.user_api_key:
        return st.session_state.user_api_key
    return os.getenv("LLM_API_KEY", "")


def quota_remaining() -> int | None:
    
    if st.session_state.key_mode == "own" and st.session_state.user_api_key:
        return None
    _maybe_reset_window()
    return max(0, DEFAULT_KEY_QUESTION_LIMIT - st.session_state.questions_asked)


def can_ask_question() -> bool:
    
    remaining = quota_remaining()
    return remaining is None or remaining > 0


def record_question_asked() -> None:
    """Call this AFTER a RAG question successfully runs (not on greetings/no-PDF)."""
    if st.session_state.key_mode == "default" or not st.session_state.user_api_key:
        st.session_state.questions_asked += 1


def render_key_selector() -> None:
    """
    Renders the small, non-blocking key-picker control.
    
    """
    remaining = quota_remaining()
    label = "🔑 Using your key (no limit)" if remaining is None else f"🔑 Default key ({remaining} left)"

    with st.popover(label):
        mode = st.radio(
            "API key",
            options=["default", "own"],
            format_func=lambda m: "Continue with the default key" if m == "default" else "Use my own API key",
            index=0 if st.session_state.key_mode == "default" else 1,
            key="key_mode_radio",
        )
        st.session_state.key_mode = mode

        if mode == "own":
            entered = st.text_input(
                "Your API key",
                type="password",  
                value=st.session_state.user_api_key,
                key="own_key_input",
                help="Kept only in memory for this session. Never saved to disk.",
            )
            st.session_state.user_api_key = entered
            if not entered:
                st.caption("Enter a key to use it for your questions.")
        else:
            st.caption(f"{DEFAULT_KEY_QUESTION_LIMIT} questions per 4-hour window. PDF uploads don't count.")
