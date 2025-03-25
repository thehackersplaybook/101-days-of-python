from streamlit import st
import openai
from dotenv import load_dotenv
import os
load_dotenv(override=True, dotenv_path=".env",verbose=True)

openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    st.error("Please set your OpenAI API key in the .env file.")
    st.stop()

def main():

    st.page_config(layout="wide",page_title="System Compatibility Checker",page_icon="💻")

    st.title("💻 System Compatibility Checker")
    st.caption("Check if your system is compatible with the apps!!")

    st.sidebar.header("🔧 System Compatibility Checker")
    st.sidebar.text_input("💻 Operating System", key="os")
