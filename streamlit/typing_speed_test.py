import streamlit as st
import time
import random
import textwrap

# -----------------------#
# 🎯 Constants & Config   #
# -----------------------#

TARGET_SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "Typing is a skill that improves with practice.",
    "Consistent effort brings consistent results.",
    "Discipline is the bridge between goals and achievement.",
    "Your time is limited, so don’t waste it living someone else’s life."
]

# -----------------------#
# 🧠 Utility Functions    #
# -----------------------#

def calculate_wpm(text: str, elapsed_time: float) -> float:
    words = len(text.split())
    return round((words / elapsed_time) * 60, 2) if elapsed_time > 0 else 0.0

def calculate_accuracy(user_input: str, target: str) -> float:
    matches = sum(1 for i, char in enumerate(user_input) if i < len(target) and char == target[i])
    return round((matches / len(target)) * 100, 2) if target else 0.0

def initialize_session_state(defaults: dict):
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def reset_session_state(defaults: dict):
    for key, val in defaults.items():
        st.session_state[key] = val

# -----------------------#
# 🚀 Streamlit App Logic  #
# -----------------------#

def typing_speed_tester_app():
    defaults = {
        "test_started": False,
        "start_time": 0.0,
        "target_text": "",
        "input_text": ""
    }
    initialize_session_state(defaults)

    st.title("🧠 TypeMaster: Typing Speed Tester")

    # Start Screen
    if not st.session_state.test_started:
        st.info("Click the button below to begin the typing test.")
        if st.button("Start Test"):
            st.session_state.test_started = True
            st.session_state.target_text = random.choice(TARGET_SENTENCES)
            st.session_state.start_time = time.time()
            st.session_state.input_text = ""

    # Typing Test Screen
    if st.session_state.test_started:
        st.subheader("📝 Type the following sentence:")
        st.code(textwrap.fill(st.session_state.target_text, width=60), language="markdown")

        st.session_state.input_text = st.text_area(
            "Start typing below:",
            value=st.session_state.input_text,
            height=150,
            key="typing_area"
        )

        if st.button("Submit"):
            elapsed = time.time() - st.session_state.start_time
            wpm = calculate_wpm(st.session_state.input_text, elapsed)
            accuracy = calculate_accuracy(st.session_state.input_text, st.session_state.target_text)

            st.success("✅ Test Completed!")
            st.write(f"⏱️ **Time Taken:** {round(elapsed, 2)} seconds")
            st.write(f"🚀 **Words Per Minute (WPM):** {wpm}")
            st.write(f"🎯 **Accuracy:** {accuracy}%")

            if st.button("🔁 Try Again"):
                reset_session_state(defaults)
                st.experimental_rerun()

# -----------------------#
# 🏁 Main Entrypoint     #
# -----------------------#

if __name__ == "__main__":
    typing_speed_tester_app()
