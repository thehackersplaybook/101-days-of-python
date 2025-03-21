import streamlit as st
from auxknow import AuxKnow
import asyncio
import traceback
import os
import re
import time
from dotenv import load_dotenv

load_dotenv(override=True, verbose=True, dotenv_path=".env")

auxknow = AuxKnow(api_key=os.getenv("PERPLEXITY_API_KEY"), openai_api_key=os.getenv("OPENAI_API_KEY"))

if not auxknow:
    st.error("❌ AuxKnow API Key Not Found in .env File")
    st.stop()

QUERIES_MODIFIERS = {
    "📈 Market Trends": "Analyze current financial market trends.",
    "💹 Investment Insights": "Provide investment strategies and opportunities.",
    "🌍 Macroeconomic Analysis": "Give insights on global economic policies and impacts.",
    "📊 Stock Analysis": "Analyze stock market performance and predictions."
}

MODES = {
    "⚡ Fast Mode": {"fast_mode": True},
    "🕵️‍♂️ Deep Research Mode": {"deep_research": True},
    "🤖 Auto Prompt Augmentation": {"auto_prompt_augment": True},
    "🧠 Unbiased Reasoning Mode": {"enable_unbiased_reasoning": True},
    "🚀 Auto Model Routing": {"auto_model_routing": True},
    "📌 Context Awareness Mode": {}  
}

FINANCE_KEYWORDS = [
    r"\bstock(s)?\b", r"\bmarket(s)?\b", r"\bshare(s)?\b", r"\bIPO(s)?\b", r"\bdividend(s)?\b",
    r"\btrade(s|r)?\b", r"\bforex\b", r"\bcurrency exchange\b", r"\bETF(s)?\b", r"\bindex fund(s)?\b",
    r"\bhedge fund(s)?\b", r"\bmutual fund(s)?\b", r"\bbond(s)?\b", r"\bequity\b", r"\bportfolio\b",
    r"\bcommodity trading\b", r"\boptions trading\b", r"\bfutures contract(s)?\b", r"\bderivative(s)?\b",
    r"\binterest rate(s)?\b", r"\binflation\b", r"\bdeflation\b", r"\bstagflation\b", r"\bmonetary policy\b",
    r"\bGDP\b", r"\bmacroeconomic\b", r"\bmicroeconomic\b", r"\beconomic indicator(s)?\b", r"\bcentral bank\b",
    r"\bFederal Reserve\b", r"\bquantitative easing\b", r"\bliquidity\b", r"\bcapital market(s)?\b",
    r"\balgorithmic trading\b", r"\bautomated trading\b", r"\brisk management\b", r"\basset allocation\b",
    r"\bshort selling\b", r"\bbull market\b", r"\bbear market\b", r"\bfinancial modeling\b",
    r"\bvaluation\b", r"\bcash flow\b", r"\bEBITDA\b", r"\bprofit margin\b", r"\brevenue\b",
    r"\btechnical analysis\b", r"\bfundamental analysis\b", r"\bprice action\b", r"\bcandlestick pattern(s)?\b",
    r"\bcryptocurrency\b", r"\bBitcoin\b", r"\bEthereum\b", r"\bstablecoin(s)?\b", r"\bblockchain\b",
    r"\btaxation\b", r"\bcapital gains tax\b", r"\bcorporate finance\b", r"\bfinancial regulation\b",
    r"\bSEC\b", r"\bSEBI\b", r"\binsider trading\b", r"\bfinancial fraud\b"
]

FINANCE_PATTERN = re.compile("|".join(FINANCE_KEYWORDS), re.IGNORECASE)

def is_finance_related(query: str) -> bool:
    return bool(FINANCE_PATTERN.search(query))


async def main():
    st.set_page_config(page_title="AuxKnow Finance Engine", page_icon="💰", layout="wide")
    st.markdown("""
    <style>
        body { background-color: #0e1117; }
        .stTextInput, .stSelectbox, .stTextArea { 
            border-radius: 8px; 
            border: 1px solid #4A90E2; 
            background-color: #1E1E2F; 
            color: white; 
        }
        .stButton > button { 
            border-radius: 10px; 
            background: linear-gradient(to right, #4A90E2, #007BFF); 
            color: white; 
            font-size: 18px; 
            transition: background 0.3s ease-in-out;  /* Smooth transition */
        }
        .stButton > button:hover { 
            background: linear-gradient(to right, #007BFF, #0056b3); /* Blue hover effect */
            color: white;  
            transform: scale(1.05);  /* Slight hover animation */
        }
        .stMarkdown { color: #d1d1e0; }
        .reportview-container { 
            background: rgba(255, 255, 255, 0.1); 
            border-radius: 15px; 
            padding: 20px; 
        }
        .blinking-cursor::after { content: '|'; animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0; } }
        .divider-box { 
            border-top: 3px solid #4A90E2; 
            margin: 20px 0; 
            padding-top: 10px;
        }
    </style>
    """, unsafe_allow_html=True)


    # 🚀 Header
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>💰 AuxKnow Finance Engine</h1>", unsafe_allow_html=True)
    st.caption("🚀 Real-Time Financial Insights Powered by AI")

    # Sidebar for settings
    with st.sidebar:
        st.markdown("## ⚙️ Configure Your Query")
        selected_mode = st.selectbox("🛠️ Select AI Mode", list(MODES.keys()), key="mode")
        mode_settings = MODES.get(selected_mode, {})
        query = st.selectbox("🔍 Choose an Insight Type", list(QUERIES_MODIFIERS.keys()))

        if query:
            st.markdown(f"### 📝 {QUERIES_MODIFIERS[query]}")
            prompt = st.text_area("💬 Enter your financial question:", placeholder="e.g., What is the stock market outlook for 2025?")
            submit_button = st.button("💡 Get Financial Insights")

    # Session State for Responses
    if "previous_responses" not in st.session_state:
        st.session_state.previous_responses = []

    if submit_button:
        if not prompt:
            st.error("❌ Please enter a valid financial question.")
            st.stop()

        if not is_finance_related(prompt):
            st.error("❌ Invalid query. Please ask about financial markets, stocks, or investments.")
            st.stop()

        st.subheader("📊 Financial Insights")

        response_placeholder = st.empty()
        citations_text = ""

        try:
            with st.spinner("💡 Generating Insights...",show_time=True):
                valid_mode_settings = {k: v for k, v in mode_settings.items() if k in ["fast_mode", "deep_research"]}
                final_prompt = f"{QUERIES_MODIFIERS[query]} {prompt}"

                if selected_mode == "📌 Context Awareness Mode":
                    if "auxknow_session" not in st.session_state:
                        st.session_state.auxknow_session = auxknow.create_session()
                    session = st.session_state.auxknow_session
                    response = session.ask_stream(final_prompt, **valid_mode_settings, for_citations=True)
                else:
                    response = auxknow.ask_stream(final_prompt, **valid_mode_settings, for_citations=True)

                response_text = ""
                progress_bar = st.progress(0)

                # Iterate over streamed response
                for step, partial_response in enumerate(response):
                    if partial_response and partial_response.answer:
                        response_text += partial_response.answer  # Accumulate text
                    
                        # Display progressively with blinking cursor effect
                        response_placeholder.markdown(
                            f"<p style='font-size:18px; color:white;' class='blinking-cursor'>{response_text}</p>",
                            unsafe_allow_html=True
                        )
                    
                    # Smooth progress updates
                    progress_bar.progress(min((step + 1) * 5, 100))
                    time.sleep(0.05)  # Smooth animation effect

                # Final display without cursor
                response_placeholder.markdown(
                    f"<p style='font-size:18px; color:white;'>{response_text}</p>",
                    unsafe_allow_html=True
                )

                # Store latest 5 responses with question-answer format
                st.session_state.previous_responses.append({"question": prompt, "answer": response_text})
                st.session_state.previous_responses = st.session_state.previous_responses[-5:]
                progress_bar.empty()

                if partial_response.citations:
                    citations_text = partial_response.citations

                if citations_text:
                    st.markdown("### 📖 Citations")
                    st.write(citations_text)

        except Exception as e:
            st.error(f"❌ Error while generating insights: {str(e)}")
            traceback.print_exc()

   
    with st.expander("📜 **View Previous Insights**", expanded=False):
        if not st.session_state.previous_responses:
            st.markdown("<p style='text-align: center; color: #888;'>No previous insights available.</p>", unsafe_allow_html=True)
        else:
            for entry in reversed(st.session_state.previous_responses):
                st.markdown(
                    f"<h3 style='color: #4A90E2;'>❓ Question: {entry['question']}</h3>", 
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<p style='font-size:18px; color:#d1d1e0;'>{entry['answer']}</p>", 
                    unsafe_allow_html=True
                )
                st.markdown("<div class='divider-box'></div>", unsafe_allow_html=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except Exception as e:
        st.error(f"❌ Initialization error: {str(e)}")
        traceback.print_exc()
