import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import traceback
import asyncio
import os
from auxknow import AuxKnow

load_dotenv(override=True, verbose=True)

auxknow = AuxKnow(
    perplexity_api_key=os.getenv("PERPLEXITY_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
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

    deep_research_enabled = st.sidebar.checkbox(
        "🔍 Deep Research Mode",
        help="Enable this mode for more detailed and comprehensive insights.",
    )

    fast_mode_enabled = st.sidebar.checkbox(
        "🚀 Fast Mode",
        help="Enable this mode for faster insights generation.",
    )

    if submit_button:
        if not prompt:
            st.warning("Please enter a valid prompt to generate insights.")
            return None
        if deep_research_enabled:
            auxknow.set_config(
                {
                    "answer_length_in_paragraphs": 8,
                    "lines_per_paragraph": 8,
                }
            )
        else:
            auxknow.set_config(
                {
                    "answer_length_in_paragraphs": 3,
                    "lines_per_paragraph": 3,
                }
            )
        if fast_mode_enabled:
            auxknow.set_config(
                {
                    "answer_length_in_paragraphs": 2,
                    "lines_per_paragraph": 3,
                    "fast_mode_enabled": True,
                }
            )
        else:
            auxknow.set_config(
                {
                    "answer_length_in_paragraphs": 3,
                    "lines_per_paragraph": 3,
                    "fast_mode_enabled": False,
                }
            )
        if prompt:
            if deep_research_enabled and fast_mode_enabled:
                st.warning(
                    "⚠️ Both 'Deep Research Mode' and 'Fast Mode' are enabled. They cannot work together. Please disable one of them."
                )
                return None
            with st.spinner("🔮 Generating Insights...", show_time=True):
                prompt_container = st.empty()
                container = st.empty()
                citations_container = st.empty()
                prompt_container.markdown(f"> Prompt: '{prompt}'")

                full_content = ""
                response = auxknow.ask_stream(
                    question=prompt,
                    deep_research=deep_research_enabled,
                    fast_mode=fast_mode_enabled,
                )
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
