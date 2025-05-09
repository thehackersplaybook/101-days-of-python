import streamlit as st
import os
from dotenv import load_dotenv
from gita_functions import load_bhagavad_gita_into_db
from openai_utils import validate_openai_key, ask_gita
import inspect
import time


# Set Streamlit page configuration
st.set_page_config(
    page_title="Bhagavad Gita Life Guide",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🕉️"
)

# Load environment variables
load_dotenv(dotenv_path=".env",verbose=True,override=True)

# --- Load Shlokas into ChromaDB on App Start ---
def initialize_shlokas():
    """
    Helper function to load Bhagavad Gita shlokas into ChromaDB.
    """
    if "shlokas_loaded" not in st.session_state:
        try:
            count = load_bhagavad_gita_into_db()  # Ensure this function returns the count
            if count > 0:
                st.session_state.shlokas_loaded = True
                return count  # Return the count of shlokas loaded
            else:
                st.session_state.shlokas_loaded = False
                return 0  # Return 0 if no shlokas were loaded
        except Exception as e:
            st.session_state.shlokas_loaded = False
            print(f"Error loading shlokas into ChromaDB: {e}")
            return 0  # Return 0 in case of an error
                

# Sidebar Function to Manage API Key
def sidebar_api_key_manager(unique_key_suffix="homepage"):
    """
    Sidebar for managing the OpenAI API key.
    """
    with st.sidebar:
        # Setup API Key
        st.title("🔑 API Key Management")
        openai_key = st.text_input(
            "Enter your OpenAI API Key:", 
            type="password", 
            key=f"api_key_input_sidebar_{unique_key_suffix}",
            placeholder="sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", 
            help="Get your API key from https://platform.openai.com/signup"
            )
        col1, col2 = st.columns(2)

        if col1.button("💾 Save API Key"):
            # Spinner for validating the API key
            with st.spinner("Validating API key...",show_time=True):
                is_valid = validate_openai_key(openai_key)

            if is_valid:
                st.session_state.saved_api_key = openai_key
                st.toast("OpenAI key saved successfully!", icon="✅")

                # Spinner for loading Bhagavad Gita shlokas into ChromaDB
                with st.spinner("Loading Bhagavad Gita shlokas into ChromaDB...",show_time=True):
                    # Load shlokas into ChromaDB
                    count = initialize_shlokas()

                # Check if shlokas were successfully loaded
                if st.session_state.get("shlokas_loaded", False):
                    st.success(f"✅ Successfully loaded {count} Bhagavad Gita shlokas into ChromaDB.")
                else:
                    st.error("❌ Failed to load Bhagavad Gita shlokas into ChromaDB.")
            else:
                st.error("Invalid OpenAI API key. Please check and try again.")

        if col2.button("🔄 Reset API Key"):
            with st.spinner("Resetting API key..."):
                st.session_state.saved_api_key = ""
                st.toast("OpenAI key reset successfully!", icon="✅")
        st.markdown("---")

# --- Initialize Sidebar ---
sidebar_api_key_manager()

# --- Main Content ---
st.title("🕉️ Bhagavad Gita Insight")
st.markdown("Get empathetic and practical advice inspired by the Gita's teachings for your life situatuions.")

with st.form("ask_gita_form"):
    user_input = st.text_area("🙏 What's troubling you or someone close?", height=100)
    st.text_input("🔍 Search for Shlokas", placeholder="Enter a keyword or phrase")
    submitted = st.form_submit_button("🧘‍♂️ Ask the Gita")

# Handle submission
if submitted:
    if not user_input.strip():
        st.warning("⚠️ Please enter a query to proceed.")
    elif not st.session_state.get("saved_api_key"):
        st.error("🔐 Please enter and save your OpenAI API key in the sidebar.")
    else:
        with st.spinner("📜 Seeking Gita's guidance..."):
            response = ask_gita(user_input, api_key=st.session_state.saved_api_key)
            st.markdown("### ✨ Gita's Response")
            st.markdown(response)