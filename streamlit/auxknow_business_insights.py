import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import traceback
import asyncio
import os
from auxknow import AuxKnow

# Load environment variables
load_dotenv(override=True, verbose=True)

# Initialize AuxKnow with API keys
auxknow = AuxKnow(
    perplexity_api_key=os.getenv("PERPLEXITY_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    api_key=os.getenv("PERPLEXITY_API_KEY"), 
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

async def main():
    st.set_page_config(
        page_title="AuxKnow Business Insights Agent",
        page_icon="💡",
        layout="wide",
    )
    
    # UI Layout
    st.title("⚡️ AuxKnow: Business Insights Agent (Demo)")
    st.caption("🚀 Generate unique Business Insights with the AuxKnow Platform.")
    
    st.sidebar.header("⛲️ Menu")
    st.sidebar.markdown("> Configure the agent as per your requirements.")
    
    # User input
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
            # UI Containers
            prompt_container = st.empty()
            container = st.empty()
            citations_container = st.empty()
            
            # Display Prompt
            prompt_container.markdown(f"**🔹 Prompt:** `{prompt}`")
            
            with st.spinner("🔮 Generating Insights..."):
                full_content = ""
                citations = set()  # Use a set to avoid duplicate citations
                
                try:
                    response = auxknow.ask_stream(question=prompt)
                    for chunk in response:
                        full_content += chunk.answer
                        container.markdown(full_content)  # Update content in real-time
                        
                        # Update citations as they stream in
                        if chunk.citations:
                            for citation in chunk.citations:
                                if citation not in citations:  # Avoid duplicates
                                    citations.add(citation)

                            # Convert citations to markdown
                            citations_markdown = "## 📚 Citations\n" + "\n".join(
                                [f"- [🔗 {c}]({c})" for c in citations]
                            )
                            citations_container.markdown(citations_markdown)

                except Exception as e:
                    st.error(f"❌ Error while generating insights: {str(e)}")
                    traceback.print_exc()

        else:
            st.error("⚠️ Please enter a valid prompt to generate insights.")

if __name__ == "__main__":
    try:
        asyncio.run(main())  # Runs only when executed as a script
    except RuntimeError:
        # Handles Streamlit’s async issue
        asyncio.run_coroutine_threadsafe(main(), asyncio.get_event_loop())
    except Exception as e:
        print(f"❌ Initialization error: {str(e)}")
        st.error("An error occurred when starting the app. Restart the server and try again.")
        traceback.print_exc()
