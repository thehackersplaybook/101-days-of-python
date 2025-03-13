import streamlit as st
from googletrans import Translator, LANGUAGES

# Page Configuration
st.set_page_config(
    page_title="Professional Language Translator", layout="wide", page_icon="🌐"
)

# Title
st.title("🌐 Professional Language Translator")
st.markdown("Translate text, detect languages, and convert between text and speech with ease.")

# Initialize Translator
translator = Translator()

# Sidebar for Features
st.sidebar.title("Features")
feature = st.sidebar.radio(
    "Choose a feature",
    ["Text Translation", "Speech-to-Text", "Text-to-Speech", "Translation History"]
)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []

# Function to Get Language Code
def get_language_code(language):
    return list(LANGUAGES.keys())[list(LANGUAGES.values()).index(language.lower())]

# Text Translation
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
    
    # Disable the Translate button if no text is entered
    translate_button = st.button("Translate", disabled=not text_to_translate.strip())
    
    if translate_button:
        if text_to_translate.strip():
            try:
                # Determine source language code
                src_code = (
                    "auto"
                    if source_language == "Auto-detect"
                    else get_language_code(source_language)
                )
                dest_code = get_language_code(target_language)
                
                # Perform translation
                translation = translator.translate(text_to_translate, src=src_code, dest=dest_code)
                st.success(f"**Translated Text ({target_language}):**")
                st.write(translation.text)
                
                # Add to history
                st.session_state.history.append({
                    "source_text": text_to_translate,
                    "translated_text": translation.text,
                    "source_lang": source_language,
                    "target_lang": target_language
                })
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter text to translate!")

# Translation History (optional feature)
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
