import streamlit as st
import asyncio
from googletrans import Translator, LANGUAGES

st.set_page_config(
    page_title="Professional Language Translator", layout="wide", page_icon="🌐"
)

st.title("🌐 Professional Language Translator")
st.markdown("Translate text, detect languages, and convert between text and speech with ease.")

translator = Translator()

st.sidebar.title("Features")
feature = st.sidebar.radio(
    "Choose a feature",
    ["Text Translation", "Translation History"]
)

if "history" not in st.session_state:
    st.session_state.history = []

def get_language_code(language) -> str:
    """
    Get the language code from the language name.
    Args:
        language (str): Language name.
        Returns:
        str: Language code.
        """
    return list(LANGUAGES.keys())[list(LANGUAGES.values()).index(language.lower())]

def translate_text(text, src_lang, target_lang) -> str:
    """
    Translate text from source language to target language.
    Args:
        text (str): Text to translate.
        src_lang (str): Source language code.
        target_lang (str): Target language code.
    Returns:
        str: Translated text.
        """
    with st.spinner("Translating Language"):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        translation = loop.run_until_complete(translator.translate(text, src=src_lang, dest=target_lang))
        return translation.text

if feature == "Text Translation":
    st.header("Text Translation")
    
    text_to_translate = st.text_area("Enter text to translate:", placeholder="Type something here...")

    source_language = st.selectbox(
        "Select source language:",
        ["Auto-detect"] + [lang.capitalize() for lang in LANGUAGES.values()]
    )

    target_language = st.selectbox(
        "Select target language:",
        [lang.capitalize() for lang in LANGUAGES.values()]
    )

    translate_button = st.button("Translate", disabled=not text_to_translate.strip())

    if translate_button:
        if text_to_translate.strip():
            try:
                src_code = "auto" if source_language == "Auto-detect" else get_language_code(source_language)
                dest_code = get_language_code(target_language)

                translated_text = translate_text(text_to_translate, src_code, dest_code)

                st.success(f"**Translated Text ({target_language}):**")
                st.write(translated_text)

                st.session_state.history.append({
                    "source_text": text_to_translate,
                    "translated_text": translated_text,
                    "source_lang": source_language,
                    "target_lang": target_language
                })

            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter text to translate!")

if feature == "Translation History":
    st.header("Translation History")

    if st.session_state.history:
        for i, entry in enumerate(st.session_state.history):
            st.write(f"**{i+1}. Source ({entry['source_lang']}):** {entry['source_text']}")
            st.write(f"**Translated ({entry['target_lang']}):** {entry['translated_text']}")
            st.markdown("---")

        if st.button("Clear History"):
            st.session_state.history = []
            st.success("Translation history cleared!")
    else:
        st.info("No translations yet!")
