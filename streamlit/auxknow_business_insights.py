import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import traceback
import asyncio
import os
from auxknow import AuxKnow

load_dotenv(override=True, verbose=True)

auxknow = AuxKnow(
    api_key=os.getenv("PERPLEXITY_API_KEY"), openai_api_key=os.getenv("OPENAI_API_KEY")
)


async def main():
    st.set_page_config(
        page_title="AuxKnow Business Insights Agent",
        page_icon="💡",
        layout="wide",
    )
    st.title("⚡️ AuxKnow: Business Insights Agent (Demo)")
    st.caption("🚀 Generate unique Business Insights with the AuxKnow Platform.")
    st.sidebar.header("⛲️ Menu")
    st.sidebar.markdown("> Configure the agent as per your requirements.")

    prompt = st.sidebar.text_area(
        "What business topic do you want insights on?",
        placeholder="AI in the Deep Tech Industry.",
    )

    submit_button = st.sidebar.button("🔮 Run Magic!")

    if submit_button:
        if prompt:
            prompt_container = st.empty()
            container = st.empty()
            citations_container = st.empty()
            prompt_container.markdown(f"> Prompt: '{prompt}'")
            with st.spinner("🔮 Generating Insights..."):
                full_content = ""
                response = auxknow.ask_stream(question=prompt)
                citations = []
                for chunk in response:
                    full_content += chunk.answer
                    if len(citations) == 0:
                        citations = chunk.citations
                        citations_markdown = "## 📚 Citations!"
                        for citation in citations:
                            citations_markdown += f"\n- [🔗 {citation}]({citation})\n"
                        citations_container.markdown(citations_markdown)

                    container.write(full_content)

        else:
            st.error("Please enter a valid prompt to generate insights.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Initialization error: {str(e)}")
        st.error(
            f"An error occurredd when starting the app. Please restart the server."
        )
        traceback.print_exc()
