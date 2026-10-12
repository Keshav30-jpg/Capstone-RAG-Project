# test_key_manager.py - temporary. Tests quota logic without running Streamlit,
# by faking session_state with a plain dict-like object.
import time
import streamlit as st

# Streamlit's session_state can be used as an object OR a dict outside a real
# app context in recent versions; if this errors on your machine, that's a
# sign we genuinely need the full app to test this part - that's fine, skip
# ahead to Step 9 and we'll verify it there instead.

from rag import key_manager as km

km.init_key_state()
print(f"Initial: mode={st.session_state.key_mode}, "
      f"questions_asked={st.session_state.questions_asked}, "
      f"quota_remaining={km.quota_remaining()}")

# Simulate asking questions until the cap is hit.
for i in range(12):
    allowed = km.can_ask_question()
    if allowed:
        km.record_question_asked()
    print(f"Question {i+1}: allowed={allowed}, remaining_after={km.quota_remaining()}")

# Simulate the 4-hour window expiring by manually rewinding window_start_time.
print("\n--- Simulating 4+ hours passing ---")
st.session_state.window_start_time = time.time() - (km.WINDOW_SECONDS + 1)
print(f"quota_remaining after window reset: {km.quota_remaining()}")

# Simulate switching to the user's own key -> should report no cap (None).
print("\n--- Switching to own key ---")
st.session_state.key_mode = "own"
st.session_state.user_api_key = "sk-fake-test-key"
print(f"quota_remaining with own key: {km.quota_remaining()}")  # expect None
print(f"can_ask_question with own key: {km.can_ask_question()}")  # expect True