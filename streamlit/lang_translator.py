import streamlit as st
from googletrans import Translator, LANGUAGES
import pyttsx3
import os
import base64
import speech_recognition as sr

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
    
    if st.button("Translate"):
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

# Speech-to-Text
elif feature == "Speech-to-Text":
    st.header("Speech-to-Text")
    st.markdown("Upload an audio file, and we will convert it to text.")
    
    uploaded_file = st.file_uploader("Upload audio file (WAV format):", type=["wav"])
    
    if uploaded_file is not None:
        recognizer = sr.Recognizer()
        with sr.AudioFile(uploaded_file) as source:
            audio = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio)
            st.success("Converted Text:")
            st.write(text)
        except Exception as e:
            st.error(f"Error in speech recognition: {e}")

# Text-to-Speech
elif feature == "Text-to-Speech":
    st.header("Text-to-Speech")
    
    text_to_convert = st.text_area("Enter text to convert to speech:")
    language = st.selectbox("Select language:", [lang.capitalize() for lang in LANGUAGES.values()])
    
    if st.button("Convert to Speech"):
        if text_to_convert.strip():
            try:
                # Initialize the pyttsx3 engine
                engine = pyttsx3.init()

                # Set the properties for speed
                rate = engine.getProperty('rate')  # Get the current speech rate
                engine.setProperty('rate', rate )  # Multiply the rate by 5 for faster speech
                
                # Save the speech to a file
                audio_file = "output.mp3"
                engine.save_to_file(text_to_convert, audio_file)
                engine.runAndWait()  # Run the speech engine

                # Play Audio
                with open(audio_file, "rb") as file:
                    audio_bytes = file.read()
                    b64 = base64.b64encode(audio_bytes).decode()
                    href = f'<a href="data:audio/mp3;base64,{b64}" download="translated_audio.mp3">Download Audio</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.audio(audio_bytes, format="audio/mp3")
                
                # Clean up
                os.remove(audio_file)
            except Exception as e:
                st.error(f"Error in text-to-speech conversion: {e}")
        else:
            st.warning("Please enter text to convert!")


# Translation History
elif feature == "Translation History":
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

#Footer
st.markdown(
        """
        <style>
        .bottom-right {
            position: fixed;
            bottom: 10px;
            right: 15px;
            font-size: 0.9em;
            color: gray;
        }
        </style>
        <div class="bottom-right">
            Made with ⚡ at 'The Hackers Playbook' ©. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True
                )

